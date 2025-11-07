from __future__ import annotations

import json
import os
import pickle
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Literal

import pandas as pd
from jsonschema import Draft202012Validator
from openai import OpenAI
from pydantic import BaseModel, BeforeValidator, Field

from app.core.settings import settings
from app.util.logger import logger

SOURCE_FILE = "./app/misc/251104 Formulieren IOAZ BBZ.xlsx"

JsonSchemaDataType = Literal["string", "integer", "boolean", "array", "object", "number"]
FunctionalDataTypes = Literal["string", "select", "multiselect", "currency", "date", "float", "boolean"]
SheetNames = Literal["BBZ-aanvraag", "BBZ-verlenging aanvraag", "IOAZ-aanvraag"]


class AiConverter:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.state_file = Path("./app/scripts/json_schema_options_dict.pkl")
        self.cache = self.load_cache()

    def load_cache(self):
        if self.state_file.exists():
            with open(self.state_file, "rb") as f:
                return pickle.load(f)
        return {}  # start with empty dict

    def save_cache_to_file(self):
        with open(self.state_file, "wb") as f:
            pickle.dump(self.cache, f)

    def __update_dict(self, input_str: str, output: list[str]):
        if input_str not in self.cache.keys():
            self.cache[input_str] = output
            self.save_cache_to_file()

    def get_options_from_raw_string(self, raw_string: str):
        if raw_string in self.cache.keys():
            # logger.info("Found raw string in cache. Raw string: %s", raw_string)
            return self.cache[raw_string]
        else:
            logger.info("Converting raw string to options list. Raw string: %s \n\n", raw_string)
            prompt = f"Return the possible options as a list of strings. If there is no list, return an empty list `[]`.\n\nThe raw options: {raw_string}"  # noqa: E501
            response = self.client.responses.create(
                model="gpt-5-mini",
                input=prompt,
            )
            options = json.loads(response.output_text)
            assert isinstance(options, list), "The response should be a list of strings."
            logger.info("Converted options: %s", options)
            self.__update_dict(raw_string, options)
            return options


ai_converter = AiConverter()


def convert_to_list(value: Any):
    if value:
        return ai_converter.get_options_from_raw_string(value)
    else:
        return []


class FieldNode(BaseModel):
    value: str
    field_definitions: list["FieldDefinition"]


class FieldDefinition(BaseModel):
    nr: int
    category: str = Field(alias="Hoofdonderwerp")
    subcategory: str | None = Field(alias="Sub-categorie")
    field_title: str = Field(alias="Vraag/ tekst")
    data_type: str | None = Field(alias="Data type")
    options: Annotated[list[str], BeforeValidator(convert_to_list)] = Field(alias="Mogelijke antwoorden ")
    required: bool = Field(alias="Verplicht (ja/nee)")
    parent_field_number: int | None = Field(alias="Voorgaande vraag")
    parent_field_value: str | None = Field(alias="Voorgaande vraag antwoord")
    nodes: list[FieldNode] = Field(default_factory=list)

    def find_node(self, field_value: str):
        return next((n for n in self.nodes if n.value == field_value), None)

    def match_string_in_data_type(self, values: list[str]):
        if self.data_type is not None:
            return any(value.strip().lower() in self.data_type.lower() for value in values)

    @property
    def is_readonly(self):
        return self.data_type is None

    @property
    def is_child(self):
        return self.parent_field_number is not None

    @property
    def __functional_data_type(self) -> FunctionalDataTypes:
        if self.data_type is None:
            return "string"
        elif self.match_string_in_data_type(["Tekst", "string"]):
            return "string"
        elif self.match_string_in_data_type(["Getal", "decimal of float (in DB)"]):
            return "float"
        elif self.match_string_in_data_type(["Multi-select", "aanvink box"]):
            return "multiselect"
        elif self.match_string_in_data_type(["Select"]):
            return "select"
        elif self.match_string_in_data_type(["Bedrag"]):
            return "currency"
        elif self.match_string_in_data_type(["Datum", "Date", "data"]):
            return "date"
        elif self.match_string_in_data_type(["Ja/nee"]):
            return "select"
        else:
            raise NotImplementedError(
                f"Data type '{self.data_type}' is not implemented. Please add it to the FieldDefinition class."
            )

    @property
    def __corrected_options(self):
        return [self.__capitalize_word(o) for o in self.options]

    @property
    def json_schema_data_type(self) -> JsonSchemaDataType:
        json_schema_data_type_mapping: dict[FunctionalDataTypes, JsonSchemaDataType] = {
            "string": "string",
            "select": "string",
            "currency": "number",
            "date": "string",
            "float": "number",
            "multiselect": "array",
            "boolean": "boolean",
        }
        return json_schema_data_type_mapping[self.__functional_data_type]

    def __capitalize_word(self, word: str):
        """
        Returns the string in lowercase, except for the first letter which is capitalized.
        """
        return word[0].upper() + word[1:].lower()

    @property
    def is_defined_as_select_but_actually_is_boolean(self):
        options = [o.lower() for o in self.options]
        return len(options) == 2 and all(o in ["ja", "nee"] for o in options)

    @property
    def json_schema_field(self):
        schema: dict[str, str | list[str] | dict | bool] = {
            "type": "boolean" if self.is_readonly else self.json_schema_data_type,
            "readOnly": self.is_readonly,
            "x-is-child": self.is_child,
        }
        if self.__functional_data_type == "select":
            schema["enum"] = self.__corrected_options
        elif self.__functional_data_type == "date":
            schema["format"] = "date"
        elif self.__functional_data_type == "multiselect":
            schema["items"] = {"type": "string", "enum": self.options}

        return schema


class DependentFieldDefinition(BaseModel):
    """
    Represents a field on which other fields depend.
    It contains the field definition and the value that triggers the dependency.
    """

    child_field_definitions: list[FieldDefinition]
    value: str


@dataclass
class DefintitionParser:
    definitions: list[FieldDefinition]

    @property
    def categories(self):
        categories = [d.category for d in self.definitions]
        # Use dict.fromkeys to remove duplicates while preserving order
        return list(dict.fromkeys(categories))

    def get_nested_required_fields(
        self,
        field: FieldDefinition,
    ):
        """
        Returns a list of required fields that are nested under other fields
        using the 'allOf' keyword in the JSON schema.
        """

        schema: list[dict] = []

        for node in field.nodes:
            required_if = sorted([field.field_title])
            assert len(set(required_if)) == len(required_if), "Duplicate values in required_if"
            required_then = sorted([d.field_title for d in node.field_definitions])
            assert len(set(required_then)) == len(required_then), (
                f"Duplicate values in required_then for node '{node.value}' in field '{field.field_title}'"
            )

            if field.json_schema_data_type == "array":
                if_condition = {"contains": {"const": node.value}}
            else:
                if_condition = {"const": node.value}

            new_item = {
                "if": {
                    "properties": {field.field_title: if_condition},
                    "required": required_if,
                },
                "then": {
                    "required": required_then,
                },
                "else": {},
            }

            for d in node.field_definitions:
                nested_required_fields = self.get_nested_required_fields(d)
                if len(nested_required_fields) > 0:
                    new_item["then"]["allOf"] = nested_required_fields

            schema.append(new_item)

        return schema

    @property
    def json_schema(self):
        json_schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
            "required": sorted(self.categories),
        }
        for category in self.categories:
            assert category, "Category cannot be empty"
            category_fields = [d for d in self.definitions if d.category == category]
            category_field_names = [f.field_title for f in category_fields]
            duplicates = [name for name, count in Counter(category_field_names).items() if count > 1]
            for d in duplicates:
                logger.error(f"Duplicate field name '{d}' in category '{category}'")

            required = list(set([d.field_title for d in category_fields if d.required and not d.parent_field_number]))
            json_schema["properties"][category] = {
                "properties": {d.field_title: d.json_schema_field for d in category_fields},
                "type": "object",
                "required": sorted(required),
            }

            # Add the parent field definitions to the schema
            category_schema = json_schema["properties"][category]
            root_fields = [f for f in category_fields if f.parent_field_number is None]
            for field in root_fields:
                nested_required_fields = self.get_nested_required_fields(field)
                if len(nested_required_fields) > 0:
                    if "allOf" not in category_schema:
                        category_schema["allOf"] = []
                    category_schema["allOf"].extend(nested_required_fields)

        self.__validate_schema(json_schema)
        return json_schema

    @staticmethod
    def __validate_schema(schema: dict):
        Draft202012Validator.check_schema(schema)


def call_llm(prompt: str):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.create(model="gpt-5", input=prompt)
    return response.output_text


def add_child_definitions(definitions: list[FieldDefinition]):
    for f in definitions:
        child_definitions = [d for d in definitions if d.parent_field_number == f.nr]
        for c_d in child_definitions:
            if c_d.parent_field_value is None:
                logger.warning(
                    f"Parent field value for field title {c_d.field_title} is None. This might lead to issues in the schema."  # noqa: E501
                )
            else:
                field_node = f.find_node(c_d.parent_field_value.strip())
                if field_node is None:
                    field_node = FieldNode(value=c_d.parent_field_value.strip(), field_definitions=[])
                    f.nodes.append(field_node)
                field_node.field_definitions.append(c_d)

    return definitions


def get_form_definition(sheet_name: SheetNames):
    df = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name, skiprows=3).astype(
        {
            "Sub-categorie": "string",
            "Data type": "string",
            "Mogelijke antwoorden ": "string",
            "Verplicht (ja/nee)": "string",
            "Voorgaande vraag antwoord": "string",
            "Voorgaande vraag": "Int64",  # Use Int64 to allow for NaN values
        }
    )
    boolean_mapping = {
        "ja": True,
        "nee": False,
        "Ja": True,
        "Nee": False,
        "JA": True,
        "NEE": False,
    }
    df = df.dropna(subset=["Vraag/ tekst"])  # type: ignore
    df["Verplicht (ja/nee)"] = df["Verplicht (ja/nee)"].fillna("Nee").map(boolean_mapping)  # type: ignore
    df["Hoofdonderwerp"] = df["Hoofdonderwerp"].str.strip()
    list_of_dicts = df.to_dict(orient="records")
    parsed_fields = [FieldDefinition(**d) for d in list_of_dicts]  # type: ignore
    parsed_fields_with_parent_definitions = add_child_definitions([f for f in parsed_fields])

    for f in parsed_fields_with_parent_definitions:
        assert f.nr != f.parent_field_number, f"Field {f.field_title} has parent field number equal to its own number."  # noqa: E501

    return parsed_fields_with_parent_definitions


def write_json_schema(schema: dict, sheet_name: str):
    output_dir = "./app/config/form_schemas"
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{sheet_name}.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


all_sheet_names: list[SheetNames] = ["BBZ-aanvraag", "BBZ-verlenging aanvraag", "IOAZ-aanvraag"]

for sh in all_sheet_names:
    definitions_per_sheet = get_form_definition(sh)
    schema = DefintitionParser(definitions_per_sheet).json_schema
    write_json_schema(sheet_name=sh, schema=schema)
