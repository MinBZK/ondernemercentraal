<script setup lang="ts">
import type { components } from '@/api/schema'
import { sortArrayByKey } from '@/util'
import { formatTimeSlot } from '@/util/format'

const props = withDefaults(
  defineProps<{
    rowsPerPage?: number
    onlyShowSlotsWithAdvisorsAvailable?: boolean
    readOnly?: boolean
  }>(),
  {
    rowsPerPage: 10,
    onlyShowSlotsWithAdvisorsAvailable: false,
    readOnly: false,
  },
)

const { fetchAvailableAppointmentSlots, availableAppointmentSlots } = useAppointment()

fetchAvailableAppointmentSlots()

const availableAppointmentSlotsIncludingInitiallySelected = computed(() => {
  // filter on available advisors if required
  const requiredAvailableSlots = availableAppointmentSlots.value.filter(
    (s) => s.has_advisor_available || !props.onlyShowSlotsWithAdvisorsAvailable,
  )

  // check if the selected appointment is already in the available slots
  const alreadyInAvailableSlots = initialSelectedAppointment
    ? requiredAvailableSlots.some(
        (slot) => slot.start_time === initialSelectedAppointment.value?.start_time,
      )
    : false
  if (!alreadyInAvailableSlots && initialSelectedAppointment.value) {
    return [...requiredAvailableSlots, initialSelectedAppointment.value]
  } else {
    return requiredAvailableSlots
  }
})

const { isMobile } = useResponsive()

const rowsPerPage = computed(() => (isMobile.value ? 5 : props.rowsPerPage))
const page = ref<number>(0)

const paginatedSlots = computed(() => {
  return sortArrayByKey(
    availableAppointmentSlotsIncludingInitiallySelected.value,
    'start_time',
  ).slice(page.value * rowsPerPage.value, (page.value + 1) * rowsPerPage.value)
})

type AppointmentSlot = components['schemas']['AppintmentSlotWithAvailability']

const selectedAppointment = defineModel<AppointmentSlot>({ required: false })

const initialSelectedAppointment = ref<AppointmentSlot>()

watch(selectedAppointment, () => {
  if (!initialSelectedAppointment.value) {
    initialSelectedAppointment.value = selectedAppointment.value
  }
})
</script>

<template>
  <div v-for="s in paginatedSlots" :key="s['start_time']" class="flex items-center gap-2 my-4">
    <RadioButton
      :inputId="s.start_time"
      name="appointment-slot"
      :value="s"
      v-model="selectedAppointment"
      :disabled="readOnly"
    />
    <label :for="s.start_time">
      {{ formatTimeSlot(s.start_time, s.end_time) }}
    </label>
  </div>
  <Paginator
    :rows="rowsPerPage"
    :total-records="availableAppointmentSlots.length"
    :pageLinkSize="isMobile ? 3 : 5"
    @page="(e) => (page = e.page)"
  />
</template>
