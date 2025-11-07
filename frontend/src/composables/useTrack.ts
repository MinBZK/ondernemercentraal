import type { components } from '@/api/schema'

type TrackCreate = components['schemas']['TrackCreate']

const { client: apiClient } = useApiClient()

export function useTrack(trackId: Ref<string | undefined>, caseId: Ref<string | undefined>) {
  const tracks = ref<components['schemas']['Track'][]>([])

  const track = ref<components['schemas']['Track']>()

  function create(newTrack: TrackCreate, caseId: string) {
    return apiClient.POST('/api/case/{case_id}/track', {
      body: newTrack,
      params: {
        path: {
          case_id: caseId,
        },
      },
    })
  }

  function updateTrack(
    newTrack: components['schemas']['TrackUpdate'],
    trackId: string,
    caseId: string,
  ) {
    return apiClient.PUT('/api/case/{case_id}/track/{track_id}', {
      body: newTrack,
      params: {
        path: {
          track_id: trackId,
          case_id: caseId,
        },
      },
    })
  }

  async function deleteTrack(track: components['schemas']['TrackBase']) {
    return apiClient.DELETE('/api/case/{case_id}/track/{track_id}', {
      params: {
        path: {
          track_id: track.id,
          case_id: track.case_id,
        },
      },
    })
  }

  async function fetchMany() {
    const { data } = await apiClient.GET('/api/track', {
      params: {
        query: {
          case_id: caseId?.value,
        },
      },
    })
    if (!data) throw new Error('No data found')
    tracks.value = data
  }

  async function fetch() {
    if (!trackId?.value) throw new Error('Track id is required')
    const { data } = await apiClient.GET('/api/track/{track_id}', {
      params: {
        path: {
          track_id: trackId.value,
          case_id: caseId?.value,
        },
      },
    })
    if (!data) throw new Error('No data found')
    track.value = data
  }

  async function updateTrackPartnerOrganization(trackId: string, partnerOrganizationName: string) {
    return apiClient.PATCH(
      '/api/track/{track_id}/partner-organization/{partner_organization_name}',
      {
        params: {
          path: {
            track_id: trackId,
            partner_organization_name: partnerOrganizationName,
          },
        },
      },
    )
  }

  async function requestPartnerOrganizationChoice() {
    if (!trackId?.value) {
      throw new Error('Track id is required')
    }
    const { data: responseMessage } = await apiClient.POST(
      '/api/track/{track_id}/partner-organization-choice-request',
      {
        params: {
          path: {
            track_id: trackId.value,
          },
        },
      },
    )
    if (!responseMessage) {
      throw new Error('No response message returned from the server')
    }
    return responseMessage
  }

  return {
    create,
    updateTrack,
    deleteTrack,
    fetchMany,
    tracks,
    fetch,
    track,
    updateTrackPartnerOrganization,
    requestPartnerOrganizationChoice,
  }
}
