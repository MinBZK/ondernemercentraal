import type { components } from '@/api/schema'

const { client } = useApiClient()

export function useForms(
  trackId: Ref<string | undefined>,
  appointmentId: Ref<string | undefined>,
  requestId: Ref<string | undefined>,
) {
  const loading = ref(true)

  const forms = ref<components['schemas']['FormData'][]>([])

  async function fetchMany() {
    loading.value = true
    const { data } = await client.GET('/api/form-data', {
      params: {
        query: {
          track_id: trackId.value || null,
          appointment_id: appointmentId.value || null,
          request_id: requestId.value || null,
        },
      },
    })
    loading.value = false
    if (!data) {
      throw new Error('No data returned from API')
    }
    forms.value = data
  }

  function createForm(
    formTemplateName: components['schemas']['FormData']['form_template_name'],
    formDataUpsert: components['schemas']['FormDataUpsert'],
  ) {
    return client.POST('/api/form-data/', {
      body: formDataUpsert,
      params: {
        query: {
          appointment_id: appointmentId.value || null,
          track_id: trackId.value || null,
          request_id: requestId.value || null,
          form_name: formTemplateName,
        },
      },
    })
  }

  function updateForm(formDataId: string, formDataUpsert: components['schemas']['FormDataUpsert']) {
    return client.PUT('/api/form-data/{form_data_id}', {
      body: formDataUpsert,
      params: {
        path: {
          form_data_id: formDataId,
        },
      },
    })
  }

  return { fetchMany, createForm, updateForm, forms, loading }
}
