import type { components } from '@/api/schema'
import type { JSONSchemaPayload } from '@/components/JSONSchemaForm/types'

const { client } = useApiClient()

export function useFormData(formDataId: Ref<string | undefined>) {
  const formData = ref<components['schemas']['FormData']>()
  const loading = ref(false)

  async function fetch() {
    if (!formDataId.value) {
      throw new Error('formDataId is undefined')
    }
    loading.value = true
    const { data } = await client.GET('/api/form-data/{form_data_id}', {
      params: {
        path: {
          form_data_id: formDataId.value,
        },
      },
    })
    if (!data) {
      throw new Error('No data returned from API')
    }
    loading.value = false
    formData.value = data
  }

  const editAllowed = computed(
    () => !formData.value || (formData.value && formData.value?.status == 'Gestart'),
  )

  const initialized = ref(false)
  watch(
    loading,
    () => {
      if (!loading.value) {
        initialized.value = true
      }
    },
    {
      immediate: true,
    },
  )

  const formDataPayload = computed(() => formData.value?.visible_payload as JSONSchemaPayload)

  const formPayload = ref<JSONSchemaPayload>()
  watch(
    formDataPayload,
    (newPayload) => {
      formPayload.value = newPayload
    },
    {
      deep: true,
      immediate: true,
    },
  )

  function updateFormStatus(status: components['schemas']['FormData']['status']) {
    if (!formDataId.value) {
      throw new Error('formDataId is undefined')
    }
    return client.PUT('/api/form-data/{form_data_id}/status/{form_status}', {
      params: {
        path: {
          form_data_id: formDataId.value,
          form_status: status,
        },
      },
    })
  }

  return { formData, fetch, editAllowed, loading, formPayload, initialized, updateFormStatus }
}
