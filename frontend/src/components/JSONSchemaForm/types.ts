import type { JSONSchema7Definition, JSONSchema7 } from 'json-schema'

export type JSONSchemaDefinitions = Record<string, JSONSchema7Definition>
export type JSONSchemaProperties = JSONSchemaDefinitions

type FieldValueTypePrimitive = string | number | JSONSchemaPayload | undefined | boolean
export type FieldValueTypes = FieldValueTypePrimitive | FieldValueTypePrimitive[] | null

export interface JSONSchemaPayload extends Record<string, FieldValueTypes> {
  // Add a placeholder property to make the interface distinct
  // This property is not strictly required in the data, but it helps TypeScript
  // without this you will get typescript errors.
  _?: string
}

export type ParentField = {
  fieldName: string
  fieldValue: string
  requiredChildFieldName: string
}

export type GenesysField = {
  fieldName: string
  jsonSchemaField: JSONSchema7
  isChild: boolean
}
