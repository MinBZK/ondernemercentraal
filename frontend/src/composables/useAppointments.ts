import type { components } from '@/api/schema'

const { client } = useApiClient()

export function useAppointments(caseId?: Ref<string | undefined>) {
  const appointments = ref<components['schemas']['Appointment'][]>([])

  async function fetchMany() {
    const { data } = await client.GET('/api/appointment/', {
      params: {
        query: {
          case_id: caseId?.value,
        },
      },
    })
    if (!data) throw new Error('No data found')
    appointments.value = data
  }

  return {
    fetchMany,
    appointments,
  }
}
