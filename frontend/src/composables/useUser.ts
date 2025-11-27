import type { components } from '@/api/schema'

const { client: apiClient } = useApiClient()

const users = ref<components['schemas']['User'][]>([])

export function useUser() {
  async function fetchMany() {
    const { data } = await apiClient.GET('/api/user/')
    if (!data) throw new Error('No users returned')
    users.value = data
  }

  function create(userCreate: components['schemas']['UserCreate']) {
    return apiClient.POST('/api/user/', {
      body: userCreate,
    })
  }

  function update(userId: string, userUpdate: components['schemas']['UserUpdate']) {
    return apiClient.PUT('/api/user/{user_id}', {
      body: userUpdate,
      params: {
        path: {
          user_id: userId,
        },
      },
    })
  }

  async function deleteUser(userId: string) {
    return apiClient.DELETE('/api/user/{user_id}', {
      params: {
        path: {
          user_id: userId,
        },
      },
    })
  }

  async function resetPassword(userId: string) {
    const { data } = await apiClient.POST('/api/user/{user_id}/reset-password', {
      params: {
        path: {
          user_id: userId,
        },
      },
    })
    if (!data) throw new Error('No password reset data returned')
    return data
  }

  return { users, create, update, deleteUser, fetchMany, resetPassword }
}
