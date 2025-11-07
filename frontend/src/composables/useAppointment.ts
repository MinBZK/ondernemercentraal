import type { components } from '@/api/schema'
import { format } from 'date-fns'

const { client } = useApiClient()

type AppointmentSlot = components['schemas']['AppintmentSlotWithAvailability']
const availableAppointmentSlots = ref<AppointmentSlot[]>([])

export function useAppointment(appointmentId?: Ref<string | undefined>) {
  const appointment = ref<components['schemas']['Appointment']>()

  const startDate = ref<Date>(new Date())
  const endDate = ref<Date>(new Date(new Date().setDate(new Date().getDate() + 14)))

  async function fetchAvailableAppointmentSlots() {
    const { data } = await client.GET('/api/appointment-slot/', {
      params: {
        query: {
          start_date: format(startDate.value, 'yyyy-MM-dd'),
          end_date: format(endDate.value, 'yyyy-MM-dd'),
        },
      },
    })
    if (!data) throw new Error('No appointment slots returned')
    availableAppointmentSlots.value = data
    return data
  }

  async function createAppointment(
    caseId: string,
    appointmentNew: components['schemas']['AppointmentNew'],
  ) {
    const { response } = await client.POST('/api/appointment/', {
      body: appointmentNew,
      params: {
        query: {
          case_id: caseId,
        },
      },
    })
    if (!response.ok) throw new Error('No appointment created')
    return
  }

  async function createAppointmentPublic(token: string, startTime: string, endTime: string) {
    const { response } = await client.POST('/api/appointment-public/', {
      params: {
        query: {
          token,
          start_time: startTime,
          end_time: endTime,
        },
      },
    })
    if (!response.ok) throw new Error('No appointment created')
    return
  }

  async function deleteAppointment(appointmentId: string) {
    return client.DELETE('/api/appointment/{appointment_id}', {
      params: {
        path: {
          appointment_id: appointmentId,
        },
      },
    })
  }

  async function updateAppointment(
    appointmentId: string,
    appointmentUpdate: components['schemas']['AppointmentUpdate'],
  ) {
    return client.PUT('/api/appointment/{appointment_id}', {
      body: appointmentUpdate,
      params: {
        path: {
          appointment_id: appointmentId,
        },
      },
    })
  }

  async function fetch() {
    if (!appointmentId?.value) {
      throw new Error('No appointment ID provided')
    }
    const { data } = await client.GET('/api/appointment/{appointment_id}', {
      params: {
        path: {
          appointment_id: appointmentId.value,
        },
      },
    })
    appointment.value = data
  }

  return {
    fetchAvailableAppointmentSlots,
    createAppointmentPublic,
    createAppointment,
    deleteAppointment,
    updateAppointment,
    startDate,
    endDate,
    availableAppointmentSlots,
    appointment,
    fetch,
  }
}
