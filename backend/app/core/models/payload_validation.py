import re
from dataclasses import dataclass
from typing import Any, Literal, TypedDict, cast

from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field, computed_field

from app.util.logger import logger

JsonSchemaDataTypes = Literal["date", "integer"]

JsonSchemaValidators = Literal[
    "$recursiveRef",
    "$ref",
    "additionalItems",
    "additionalProperties",
    "allOf",
    "anyOf",
    "const",
    "contains",
    "dependentRequired",
    "dependentSchemas",
    "enum",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "format",
    "if",
    "items",
    "maxItems",
    "maxLength",
    "maxProperties",
    "maximum",
    "minItems",
    "minLength",
    "minProperties",
    "minimum",
    "multipleOf",
    "not",
    "oneOf",
    "pattern",
    "patternProperties",
    "properties",
    "propertyNames",
    "required",
    "type",
    "unevaluatedItems",
    "unevaluatedProperties",
    "uniqueItems",
]


class RequiredProperty(TypedDict):
    field: str
    readable_message: str


class PayloadValidationError(BaseModel):
    message: str
    absolute_schema_path: list[str | int]
    validator: JsonSchemaValidators | None
    json_schema: dict = Field(exclude=True)

    @classmethod
    def __get_single_value_from_regex(cls, regex_pattern: str, value: str) -> str | None:
        match = re.search(regex_pattern, value)
        if match is not None:
            extracted_string = match.group(1)
            return extracted_string

    @classmethod
    def __get_single_value_from_regex_patterns(cls, regex_patterns: list[str], value: str):
        results = [cls.__get_single_value_from_regex(p, value) for p in regex_patterns]
        return results

    @staticmethod
    def __get_multiple_values_from_regex(regex_pattern: str, value: str) -> list[str]:
        matches = re.findall(regex_pattern, value)
        return matches

    def __parse_additional_properties_error(self) -> str | None:
        additional_property_singular = self.__get_single_value_from_regex(r"'([^']+)' was unexpected", self.message)

        if additional_property_singular is None:
            additional_property_plural = self.__get_multiple_values_from_regex(r"'([A-Za-z]+)'", self.message)
            additional_property_plural_str = ", ".join([f"'{v}'" for v in additional_property_plural])
            return f"Velden {additional_property_plural_str} zijn niet toegestaan"
        else:
            return f"Veld '{additional_property_singular}' is niet toegestaan"

    def __parse_date_format_error(self) -> str | None:
        target_value = self.__get_single_value_from_regex(r"'([^']+)' is not a 'date'", self.message)
        if target_value:
            return f"Waarde '{target_value}' is geen geldige waarde voor dit veld met datatype 'datum'"

    def __parse_data_type_error(self, data_type: JsonSchemaDataTypes) -> str | None:
        target_value = self.__get_single_value_from_regex(rf"'([^']+)' is not of type '{data_type}'", self.message)
        alias_dict: dict[JsonSchemaDataTypes, str] = {"integer": "geheel getal"}
        if target_value:
            alias = alias_dict.get(data_type, data_type)
            return f"Waarde '{target_value}' is geen geldige waarde voor dit veld met datatype '{alias}'"

    def __parse_required_property_error(self) -> RequiredProperty | None:
        pattern_single_quote = r"'([^']+)' is a required property"
        pattern_double_quote = r'"([^"]+)" is a required property'

        required_properties = self.__get_single_value_from_regex_patterns(
            [pattern_double_quote, pattern_single_quote], self.message
        )
        required_property = next((p for p in required_properties if p is not None), None)

        # Encode required property to make sure new line characters are handled correctly
        if required_property:
            required_property = (
                required_property.encode("latin1", errors="ignore").decode("cp1252").replace("\\n", "\n")
            )

        if required_property:
            return {
                "field": required_property,
                "readable_message": f"Veld '{required_property}' is verplicht",
            }
        else:
            logger.error(
                f"No required property found in '{self.message}', '{self.validator}' and '{self.absolute_schema_path}'"
            )
            return

    def __parse_anyof_error(self) -> str | None:
        """
        Returns a readable error message when given a set of fields, only one is allowed to have a value.

        - This has been implemented in the JSON Schema using the 'anyOf' operator.
        - This parsing function has a very tight coupling to this specific implementation.
        - Other "oneOf" schema definitions may be possible that have a completely different purpose,
          this parser will not be applicable in such cases.

        The following schema was used when writing this parser:

        {
        ...,
            "anyOf": [
                {
                "required": [
                    "Datum besluit"
                ],
                "not": {
                    "required": [
                    "Datum afhandeling zonder besluit"
                        ]
                    }
                },
                {
                "required": [
                    "Datum afhandeling zonder besluit"
                ],
                "not": {
                    "required": [
                    "Datum besluit"
                        ]
                    }
                },
                {
                "not": {
                    "required": [
                    "Datum besluit",
                    "Datum afhandeling zonder besluit"
                        ]
                    }
                }
            ]
        }
        """

        relevant_schema = self.json_schema.get(self.validator, None)
        if type(relevant_schema) is list and relevant_schema is not None and len(relevant_schema) > 0:
            relevant_schema_item = relevant_schema[0]
            expected_keys = ["required", "not"]
            expected_keys_present = [e for e in expected_keys if e in relevant_schema_item.keys()]
            if expected_keys_present:
                relevant_fields = relevant_schema_item.get("required", None) + relevant_schema_item.get("not", {}).get(
                    "required"
                )
                stringified_field_names = ", ".join([f"'{field}'" for field in relevant_fields])
                return f"De volgende velden mogen niet tegelijk zijn ingevuld: {stringified_field_names}"

    def __parse_enum_error(self) -> str | None:
        pattern = r"'(.*?)' is not one of \[(.*?)\]|\b(\d+)\b is not one of \[(.*?)\]"
        match = re.search(pattern, self.message)

        received_value_is_int = match is not None and match.group(3) is not None

        if match:
            first_group = 3 if received_value_is_int else 1
            received_value = match.group(first_group)
            allowed_values = [s.strip() for s in match.group(first_group + 1).split(",")]
            allowed_values_str = ", ".join(allowed_values)
            return f"Waarde '{received_value}' is niet toegestaan, alleen de volgende waardes zijn toegestaan: {allowed_values_str}"  # noqa

    @property
    def required_property(self):
        if self.validator == "required":
            return self.__parse_required_property_error()

    @computed_field
    @property
    def readable_message(self) -> str:
        parsed_error_message = None

        if self.validator == "additionalProperties":
            parsed_error_message = self.__parse_additional_properties_error()
        elif self.validator == "format" and "date" in self.message:
            parsed_error_message = self.__parse_date_format_error()
        elif self.validator == "type" and "integer" in self.message:
            parsed_error_message = self.__parse_data_type_error(data_type="integer")
        elif self.validator == "required":
            parsed_error_message = self.required_property["readable_message"] if self.required_property else None
        elif self.validator == "enum":
            parsed_error_message = self.__parse_enum_error()
        elif self.validator == "anyOf":
            parsed_error_message = self.__parse_anyof_error()
        else:
            logger.error(
                f"No parser defined for '{self.message}', '{self.validator}' and '{self.absolute_schema_path}'"
            )

        if parsed_error_message is None:
            return f"{self.message} (validator: '{self.validator}', locatie: '{self.absolute_schema_path}')"  # noqa
        else:
            return parsed_error_message


class PayloadValidation(BaseModel):
    jsonschema: dict = Field(exclude=True)
    payload: dict = Field(exclude=True)

    def __get_errors(self, payload: dict):
        return list(Draft202012Validator(self.jsonschema).iter_errors(payload))

    def __parse_jsonschema_error(self, error: Any):
        return PayloadValidationError(
            message=error.message,
            json_schema=self.jsonschema,
            absolute_schema_path=list(error.absolute_schema_path),
            validator=cast(JsonSchemaValidators, str(error.validator)),
        )

    @property
    def errors(self):
        """
        Returns a list of errors.

        The payload does NOT include readonly properties (modeled as boolean) that are set to true.
        """
        return self.__get_errors(self.payload)

    @computed_field
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @computed_field
    @property
    def validation_errors(self) -> list[PayloadValidationError]:
        return [self.__parse_jsonschema_error(e) for e in self.errors]

    @computed_field
    @property
    def required_properties(self) -> list[str]:
        return [e.required_property["field"] for e in self.validation_errors if e.required_property is not None]


@dataclass
class ParsedJsonSchemaField:
    """
    Returns information about a field in a JSON schema based on the key and the schema itself.
    """

    name: str
    jsonschema: dict

    @property
    def nested_json_schema(self):
        assert self.name in self.jsonschema["properties"], (
            f"Field '{self.name}' not found in JSON schema: {self.jsonschema}"
        )  # noqa
        return self.jsonschema["properties"][self.name]

    @property
    def is_readonly(self):
        return self.nested_json_schema.get("readOnly", False)

    @property
    def is_object(self):
        return self.nested_json_schema.get("type", None) == "object"


@dataclass
class JsonSchemaPayloadParser:
    payload: dict
    jsonschema: dict

    @staticmethod
    def get_parsed_fields(jsonschema: dict):
        return [ParsedJsonSchemaField(name=k, jsonschema=jsonschema) for k in jsonschema["properties"].keys()]

    def __get_adjusted_payload(self, payload: dict, jsonschema: dict):
        """
        Adjusts the payload recursively.
        If a field is readonly in the schema, it will have value "true" in the payload.
        """
        parsed_fields = self.get_parsed_fields(jsonschema)
        available_keys = set(payload.keys())
        readonly_keys = set([f.name for f in parsed_fields if f.is_readonly])
        missing_readonly_keys = readonly_keys - available_keys

        payload_adjusted = {}
        for k, v in payload.items():
            parsed_field = ParsedJsonSchemaField(name=k, jsonschema=jsonschema)
            if parsed_field.is_readonly:
                payload_value = True
            elif parsed_field.is_object:
                payload_value = self.__get_adjusted_payload(v, parsed_field.nested_json_schema)
            else:
                payload_value = v
            payload_adjusted[k] = payload_value

        for k in missing_readonly_keys:
            payload_adjusted[k] = True

        return payload_adjusted

    @property
    def payload_adjusted(self):
        return self.__get_adjusted_payload(self.payload, self.jsonschema)


class PayloadValidationWrapper(BaseModel):
    jsonschema: dict = Field(exclude=True)
    payload: dict = Field(exclude=True)

    def __get_validation(self, payload: dict):
        return PayloadValidation(jsonschema=self.jsonschema, payload=payload)

    @property
    def validation_default(self):
        return self.__get_validation(self.payload)

    @property
    def validation_empty_payload(self):
        return self.__get_validation({})

    @property
    def payload_adjusted(self):
        return JsonSchemaPayloadParser(payload=self.payload, jsonschema=self.jsonschema).payload_adjusted

    @property
    def validation_adjusted(self):
        return self.__get_validation(self.payload_adjusted)

    @computed_field
    @property
    def is_valid(self) -> bool:
        """
        Checks whether a payload is valid against the JSON schema based on an adjusted payload.
        """
        return self.validation_adjusted.is_valid

    @computed_field
    @property
    def validation_errors(self) -> list[PayloadValidationError]:
        """
        Returns validation errors for the adjusted payload.
        """
        return self.validation_adjusted.validation_errors

    @computed_field
    @property
    def required_properties(self) -> list[str]:
        """
        Returns a list of properties that are *always* required, even when the payload is empty.
        """
        required_properties_empty_payload = self.__get_validation({}).required_properties
        required_properties_current_payload = self.__get_validation(self.payload).required_properties

        required_properties_dynamic: list[str] = []

        for p in self.payload.keys():
            payload_corrected = self.payload.copy()
            del payload_corrected[p]
            required_properties_for_corrected_payload = self.__get_validation(payload_corrected).required_properties
            if p in required_properties_for_corrected_payload:
                required_properties_dynamic.append(p)

        return list(
            set(required_properties_empty_payload + required_properties_current_payload + required_properties_dynamic)
        )
