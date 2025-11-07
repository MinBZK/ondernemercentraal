import type { components } from '@/api/schema'

const cases = ref<components['schemas']['CaseWithClientAndAdvisor'][]>([])
const { client: apiClient } = useApiClient()
const clientCase = ref<components['schemas']['Case']>()

export function useCase(caseId?: Ref<string>) {
  async function fetchCases() {
    const { data } = await apiClient.GET('/api/case/')
    if (!data) throw new Error('No cases returned')
    cases.value = data
  }

  async function fetch() {
    if (!caseId?.value) {
      throw new Error('Case ID is required to fetch a case')
    }
    const { data } = await apiClient.GET('/api/case/{case_id}', {
      params: {
        path: {
          case_id: caseId.value,
        },
      },
    })
    if (!data) throw new Error('No case returned')
    clientCase.value = data
  }

  async function updateAdvisor(caseId: string, advisorId?: string) {
    return await apiClient.PATCH('/api/case/{case_id}/advisor', {
      params: {
        query: {
          advisor_id: advisorId,
        },
        path: {
          case_id: caseId,
        },
      },
    })
  }

  async function deleteCase(caseId: string) {
    return await apiClient.DELETE('/api/case/{case_id}', {
      params: {
        path: {
          case_id: caseId,
        },
      },
    })
  }

  return { cases, clientCase, deleteCase, fetch, fetchCases, updateAdvisor }
}
