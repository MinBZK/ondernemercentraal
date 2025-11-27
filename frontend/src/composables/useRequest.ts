import type { components } from '@/api/schema'

const requests = ref<components['schemas']['Request'][]>([])

const { client: ApiClient } = useApiClient()

export function useRequest(caseId: Ref<string>) {
  async function fetch() {
    const { data } = await ApiClient.GET('/api/case/{case_id}/request/', {
      params: {
        path: {
          case_id: caseId?.value,
        },
      },
    })
    if (!data) {
      throw new Error('Failed to fetch requests')
    }
    requests.value = data
  }

  function updateRequest(payload: components['schemas']['RequestUpsert'], requestId: string) {
    return ApiClient.PUT('/api/case/{case_id}/request/{request_id}', {
      params: {
        path: {
          case_id: caseId.value,
          request_id: requestId,
        },
      },
      body: payload,
    })
  }

  function createRequest(payload: components['schemas']['RequestUpsert']) {
    return ApiClient.POST('/api/case/{case_id}/request', {
      body: payload,
      params: {
        path: {
          case_id: caseId.value,
        },
      },
    })
  }

  function deleteRequest(requestId: string) {
    return ApiClient.DELETE('/api/case/{case_id}/request/{request_id}', {
      params: {
        path: {
          case_id: caseId.value,
          request_id: requestId,
        },
      },
    })
  }

  return {
    requests,
    fetch,
    createRequest,
    updateRequest,
    deleteRequest,
  }
}
