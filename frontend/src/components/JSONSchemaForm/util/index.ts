import type { JSONSchemaDefinitions, GenesysField } from '../types'
import type { JSONSchema7 } from 'json-schema'

/**
 *
 * @param schema: the schema of a field
 * @param definitions: the definitions of the global schema
 * @returns a schema were all references from '$ref' or '$ref' in 'allOf' are substituted with the schema defined in the definitions
 */

function flattenSchema(
  schema: JSONSchema7,
  definitions: JSONSchemaDefinitions | undefined,
): JSONSchema7 {
  const items = schema.items

  if (typeof items === 'boolean') return schema
  if (Array.isArray(items)) {
    console.error('Array for items not supported')
    return schema
  }

  const reference = schema.type == 'array' ? items?.$ref : schema.$ref

  if (reference && !definitions) {
    throw new Error(
      'Field has properties defined in reference, but there are no definitions defined',
    )
  }

  const flatSchema =
    reference && definitions ? getSchemaFromReference(reference, definitions) : { ...schema }

  if (flatSchema.$ref) {
    return flattenSchema(flatSchema, definitions)
  } else {
    return flatSchema
  }
}

/**
 *
 * @param pathReference a string with a reference to the schema in $defs
 * @param definitions the definitions defined in $defs or definitions
 * @returns the schema defined in 'definitions' with the key corresponding to pathReference
 */
function getSchemaFromReference(pathReference: string, definitions: JSONSchemaDefinitions) {
  const path = pathReference.split('/')
  const key = path[2]
  const schema = definitions[key] as JSONSchema7
  if (!schema) {
    console.error(`Key ${key} does not exist in definitions`, definitions)
  }
  return schema
}

function getPropertiesFromSchema(
  field: GenesysField,
  definitions: JSONSchemaDefinitions | undefined,
): JSONSchema7 | undefined {
  // if (!definitions) return
  // if (typeof definitions === 'boolean') return
  // if (typeof field.jsonSchemaField == 'boolean') return
  const schema = flattenSchema(field.jsonSchemaField, definitions)
  if (typeof schema !== 'boolean') return schema
}

export { getPropertiesFromSchema, getSchemaFromReference }
