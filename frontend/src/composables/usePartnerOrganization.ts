import type { components } from '@/api/schema'

const partnerOrganizations = ref<components['schemas']['PartnerOrganization'][]>([])

const { client: ApiClient } = useApiClient()

export function usePartnerOrganization(partnerOrganizationId?: Ref<string | undefined>) {
  async function fetch() {
    const { data } = await ApiClient.GET('/api/partner-organization/')
    if (!data) {
      throw new Error('Failed to fetch partner organizations')
    }
    partnerOrganizations.value = data
  }

  const assertedPartnerOrganizationId = computed(() => {
    if (!partnerOrganizationId?.value) {
      throw new Error('Partner organization ID is required')
    }
    return partnerOrganizationId.value
  })

  function updatePartnerOrganization(payload: components['schemas']['PartnerOrganizationUpsert']) {
    return ApiClient.PUT('/api/partner-organization/{partner_organization_id}', {
      params: {
        path: {
          partner_organization_id: assertedPartnerOrganizationId.value,
        },
      },
      body: payload,
    })
  }

  function createPartnerOrganization(payload: components['schemas']['PartnerOrganizationUpsert']) {
    return ApiClient.POST('/api/partner-organization/', { body: payload })
  }

  function deletePartnerOrganization(partnerOrganizationId: string) {
    return ApiClient.DELETE('/api/partner-organization/{partner_organization_id}', {
      params: {
        path: {
          partner_organization_id: partnerOrganizationId,
        },
      },
    })
  }

  return {
    partnerOrganizations,
    fetch,
    updatePartnerOrganization,
    createPartnerOrganization,
    deletePartnerOrganization,
  }
}
