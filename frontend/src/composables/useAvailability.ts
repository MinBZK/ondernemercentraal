import type { components } from '@/api/schema'
import { eachDayOfInterval, format, isWeekend } from 'date-fns'

const { client } = useApiClient()

const availabilityResponse = ref<components['schemas']['AvailabilityResponse']>()

export function useAvailability(startDate: Ref<Date | undefined>, endDate: Ref<Date | undefined>) {
  const days = computed(() => {
    const allDays = eachDayOfInterval({ start: startDate.value!, end: endDate.value! })
    const workingDays = allDays.filter((day) => !isWeekend(day))
    return workingDays
  })

  async function fetch() {
    if (!startDate.value) throw new Error('Start date is required')
    if (!endDate.value) throw new Error('End date is required')

    const { data } = await client.GET('/api/availability/', {
      params: {
        query: {
          start_date: format(startDate.value, 'yyyy-MM-dd'),
          end_date: format(endDate.value, 'yyyy-MM-dd'),
        },
      },
    })
    if (!data) throw new Error('No data returned')
    availabilityResponse.value = data
    return data
  }

  function updateCapacity(date: Date, slotHourStart: number, newCapacity: number) {
    return client.PATCH('/api/availability/{date}/slot/{hour_start}', {
      params: {
        path: {
          date: format(date, 'yyyy-MM-dd'),
          hour_start: slotHourStart,
        },
        query: {
          new_capacity: newCapacity,
        },
      },
    })
  }

  return { fetch, updateCapacity, days, availabilityResponse }
}
