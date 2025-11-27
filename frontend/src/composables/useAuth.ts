import type { components } from '@/api/schema'

const token = ref<string>('')

const me = ref<components['schemas']['UserWithCase']>()
const userAuthenticated = ref<boolean>(false)

const { client } = useApiClient()

async function fetchMe() {
  const { data, response } = await client.GET('/api/me')
  if (!data) throw new Error('Failed to fetch user data')
  me.value = data
  userAuthenticated.value = response.status === 200
}

export function useAuth() {
  return { token, me, fetchMe, userAuthenticated }
}
