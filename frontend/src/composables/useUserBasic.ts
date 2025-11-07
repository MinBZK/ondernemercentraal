import type { components } from '@/api/schema'

const { client: apiClient } = useApiClient()

const users = ref<components['schemas']['UserBase'][]>()

export function useUserBasic(caseId?: Ref<string | undefined>) {
  async function fetch() {
    const { data } = await apiClient.GET('/api/user-basic/', {
      params: {
        query: {
          case_id: caseId?.value,
        },
      },
    })
    if (!data) throw new Error('No users returned')
    users.value = data
  }

  return { users, fetch }
}
