import type { components } from '@/api/schema'

const { client } = useApiClient()

const config_ = ref<components['schemas']['AppConfig']>()

const baseUrl = `${window.location.origin}/beheer`

async function fetch() {
  const { data } = await client.GET('/api/config/')
  if (!data) {
    throw new Error('Failed to fetch Keycloak configuration')
  }
  config_.value = data
  return data
}

const config = computed(() => {
  if (!config_.value) {
    throw new Error('Configuration not loaded. Please call fetch() first.')
  }
  return config_.value
})

export function useConfig() {
  return { config, fetch, baseUrl }
}
