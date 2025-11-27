import type { components } from '@/api/schema'

const { client: apiClient } = useApiClient()

const roles = ref<components['schemas']['Role'][]>([])

export function useRole() {
  async function fetchMany() {
    const { data } = await apiClient.GET('/api/role/')
    if (!data) throw new Error('No users returned')
    roles.value = data
  }

  return { roles, fetchMany }
}
