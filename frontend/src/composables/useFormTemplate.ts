import type { components } from '@/api/schema'
import type { JSONSchemaPayload } from '@/components/JSONSchemaForm/types'
import type { JSONSchema7 } from 'json-schema'

const { client: ApiClient } = useApiClient()

function parsePayload(payload: Record<string, unknown> | undefined) {
  return payload ? (payload as JSONSchemaPayload) : undefined
}

export function useFormTemplate(formName: MaybeRef<components['schemas']['FormTemplate']['name']>) {
  const formTemplate = ref<components['schemas']['FormTemplate']>()

  const schema = computed(() => {
    const payload = formTemplate.value?.template_schema
    return payload ? (payload as JSONSchema7) : undefined
  })

  async function fetch() {
    formTemplate.value = undefined
    const { data } = await ApiClient.GET('/api/form-template/{form_name}', {
      params: {
        path: {
          form_name: unref(formName),
        },
      },
    })
    if (!data) {
      throw new Error('Failed to fetch form template')
    }
    formTemplate.value = data
  }

  function validateFormPayload(payload: Record<string, unknown>) {
    return ApiClient.POST('/api/form-template/{form_name}/validation', {
      body: payload,
      params: {
        path: {
          form_name: unref(formName),
        },
      },
    })
  }

  return { formTemplate, fetch, parsePayload, schema, validateFormPayload }
}
