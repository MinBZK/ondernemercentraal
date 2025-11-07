import type { components } from '@/api/schema'
import { StorageSerializers, useSessionStorage } from '@vueuse/core'

type Client = components['schemas']['ClientWithCasePublic']
const { client: apiClient } = useApiClient()
const createdClient = useSessionStorage<Client | null>('client', null, {
  serializer: StorageSerializers.object,
})

const client = ref<Client>()

export function useClient(clientId?: Ref<string | undefined>) {
  const loading = ref(false)

  async function validateLocation(appointmentLocation: components['schemas']['ClientLocation']) {
    const { data } = await apiClient.POST('/api/client/validation', {
      body: appointmentLocation,
    })
    if (!data) throw new Error('No validation returned')
    return data
  }

  async function create(
    appointmentLocation: components['schemas']['ClientLocation'],
    appointmentDetail: components['schemas']['ClientDetails'],
  ) {
    const { data, error } = await apiClient.POST('/api/client/', {
      body: {
        details: appointmentDetail,
        location: appointmentLocation,
      },
    })
    if (error) {
      console.error('Error creating client', error)
      throw new Error('Client not created')
    }
    createdClient.value = data
  }

  async function resendConfirmationEmail(clientId?: string, email?: string) {
    const { response } = await apiClient.POST('/api/client/resend-confirmation-request', {
      params: {
        query: {
          client_id: clientId,
          email: email,
        },
      },
    })
    if (response.status != 200) {
      throw new Error('No confirmation email sent')
    }
    return
  }

  async function fetchFromToken(token: string) {
    loading.value = true
    const { data } = await apiClient.GET('/api/client/client-from-token', {
      params: {
        query: {
          token,
        },
      },
    })
    createdClient.value = data
    loading.value = false
  }

  async function fetch() {
    if (!clientId?.value) {
      throw new Error('No clientId')
    }
    const { data } = await apiClient.GET('/api/client/{client_id}', {
      params: {
        path: {
          client_id: clientId.value,
        },
      },
    })
    if (!data) throw new Error('No client returned')
    client.value = data
  }

  async function createUser() {
    if (!clientId?.value) {
      throw new Error('No clientId')
    }
    const { data } = await apiClient.POST('/api/client/{client_id}/user', {
      params: {
        path: {
          client_id: clientId.value,
        },
      },
    })
    if (!data) throw new Error('No user created')
    return data
  }

  function updateClient(clientUpdate: components['schemas']['ClientUpdate']) {
    if (!clientId?.value) {
      throw new Error('No clientId')
    }
    return apiClient.PUT('/api/client/{client_id}', {
      body: clientUpdate,
      params: {
        path: {
          client_id: clientId.value,
        },
      },
    })
  }

  function confirmEmail(token: string) {
    return apiClient.POST('/api/client/{client_id}/confirm-email', {
      params: {
        query: {
          token,
        },
      },
    })
  }

  return {
    create,
    validateLocation,
    resendConfirmationEmail,
    fetchFromToken,
    fetch,
    createUser,
    updateClient,
    confirmEmail,
    createdClient,
    loading,
    client,
  }
}
