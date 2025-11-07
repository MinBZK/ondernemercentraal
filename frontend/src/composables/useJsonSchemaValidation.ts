import type { components } from '@/api/schema'
import type { JSONSchema7 } from 'json-schema'
import type { JSONSchemaPayload } from '@/components/JSONSchemaForm/types'

type PayloadValidation = components['schemas']['PayloadValidationWrapper']

const { client: ApiClient } = useApiClient()

export function useJsonSchemaValidation(
  schema: MaybeRef<JSONSchema7>,
  payload: Ref<JSONSchemaPayload | null>,
) {
  const validation = ref<PayloadValidation>()

  async function validateFormPayload() {
    const schemaParsed = (unref(schema) || {}) as { [key: string]: unknown }
    const { data } = await ApiClient.POST('/api/json-schema-validation/', {
      body: {
        payload: payload.value || {},
        jsonschema: schemaParsed,
      },
    })
    if (!data) {
      throw new Error('Failed to validate form payload')
    }
    validation.value = data
  }

  watch(
    payload,
    () => {
      validateFormPayload()
    },
    {
      immediate: true,
      deep: true,
    },
  )

  return { validation, validateFormPayload }
}
