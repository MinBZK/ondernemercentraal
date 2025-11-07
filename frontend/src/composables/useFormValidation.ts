import type { components } from '@/api/schema'

type PayloadValidation = components['schemas']['PayloadValidation']
const validation = ref<PayloadValidation>()

const { client: ApiClient } = useApiClient()

export function useFormValidation(
  formName: MaybeRef<components['schemas']['FormTemplate']['name']>,
  payload: Ref<Record<string, unknown>>,
) {
  async function validateFormPayload() {
    const { data } = await ApiClient.POST('/api/form-template/{form_name}/validation', {
      body: payload.value || {},
      params: {
        path: {
          form_name: unref(formName),
        },
      },
    })
    if (!data) {
      throw new Error('Failed to validate form payload')
    }
    validation.value = data
  }

  watch(payload, (newPayload, oldPayload) => {
    const payloadHasChanged = JSON.stringify(newPayload) !== JSON.stringify(oldPayload)
    if (payloadHasChanged) {
      validateFormPayload()
    }
  })

  return { validation, validateFormPayload }
}
