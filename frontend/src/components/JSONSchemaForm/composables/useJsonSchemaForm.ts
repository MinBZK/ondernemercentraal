import type { JSONSchema7 } from 'json-schema'
import type { GenesysField, JSONSchemaPayload, JSONSchemaDefinitions } from './../types'
import { getSchemaFromReference } from '@/components/JSONSchemaForm/util'

function notEmpty<TValue>(value: TValue | null | undefined): value is TValue {
  return value !== null && value !== undefined
}

function getFieldNames(schema: JSONSchema7) {
  return schema.properties ? Object.keys(schema.properties) : []
}

function getFieldsFromProperties(schema: JSONSchema7) {
  const fieldNames = getFieldNames(schema)
  return fieldNames
    .map((fieldName) => {
      const jsonSchemaField = getField(schema, fieldName)
      //@ts-expect-error: access custom property not defined in the JSONSchema standard
      const isChild = Boolean(jsonSchemaField?.['x-is-child'])
      if (!jsonSchemaField) return
      const field: GenesysField = {
        jsonSchemaField,
        fieldName: fieldName,
        isChild,
      }
      return field
    })
    .filter((f) => f !== undefined) as GenesysField[]
}

function getFieldsFromAllOf(
  schema: JSONSchema7,
  definitions: JSONSchemaDefinitions,
): GenesysField[] {
  const fieldsFromAllOf = schema.allOf
    ? schema.allOf
        .map((allOfValue) => {
          if (typeof allOfValue == 'boolean') return
          if (!allOfValue.$ref) return
          const schemaFromRef = getSchemaFromReference(allOfValue.$ref, definitions)
          return schemaFromRef
        })
        .filter(notEmpty)
        .map((schema) => {
          const fieldsFromAllOf = getFieldsFromAllOf(schema, definitions)
          const fieldsFromRef = getFieldsFromRef(schema, definitions)
          const fieldsFromProperties = getFieldsFromProperties(schema)
          const allFields = [...fieldsFromAllOf, ...fieldsFromRef, ...fieldsFromProperties]
          return allFields
        })
        .flat()
    : []
  return fieldsFromAllOf
}

function getFieldsFromRef(schema: JSONSchema7, definitions: JSONSchemaDefinitions) {
  if (schema.$ref && schema.definitions) {
    const referencedSchema = getSchemaFromReference(schema.$ref, definitions)
    return [
      ...getFieldsFromProperties(referencedSchema),
      ...getFieldsFromAllOf(referencedSchema, definitions),
    ]
  } else {
    return []
  }
}

function getFieldsFromSchema(schema: JSONSchema7) {
  const definitions = schema.definitions
  const fields = [
    ...(definitions ? getFieldsFromAllOf(schema, definitions) : []),
    ...(definitions ? getFieldsFromRef(schema, definitions) : []),
    ...getFieldsFromProperties(schema),
  ]

  return fields
}

function getField(schema: JSONSchema7, fieldName: string) {
  const field = schema.properties?.[fieldName]
  if (typeof field == 'boolean') {
    throw new Error(`'Field ${fieldName} is a boolean, this inot implemented yet`)
  } else {
    return field
  }
}

export function useJsonSchemaForm(jsonSchema: JSONSchema7) {
  const fieldNames = computed(() => getFieldNames(jsonSchema))

  const fields = getFieldsFromSchema(jsonSchema)

  function getCurrentValue(f: GenesysField, payload: JSONSchemaPayload | null | undefined) {
    return payload && payload[f.fieldName] ? payload[f.fieldName] : null
  }

  const paginationPossible = computed(() => {
    const isPossible = fields.map((f) => f.jsonSchemaField.type).every((type) => type == 'object')
    return isPossible
  })

  return {
    fieldNames,
    fields,
    getCurrentValue,
    paginationPossible,
  }
}
