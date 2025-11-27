import type { components } from '@/api/schema'

const trackValues = ref<components['schemas']['TrackValues']>()

const { client: ApiClient } = useApiClient()

export function useTrackValue() {
  async function fetch() {
    const { data } = await ApiClient.GET('/api/track-value/')
    if (!data) {
      throw new Error('Failed to fetch track types')
    }
    trackValues.value = data
  }

  return { trackValues, fetch }
}
