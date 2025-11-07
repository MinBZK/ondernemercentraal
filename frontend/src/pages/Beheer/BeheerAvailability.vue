<script setup lang="ts">
import { formatDate } from 'date-fns'
import { sortArrayByKey } from '@/util'

// first day of the current month
const defaultDate = new Date(new Date().getFullYear(), new Date().getMonth(), 1, 0, 0, 0, 0)

const startDate = ref<Date>(defaultDate)
const endDate = computed(() => {
  if (startDate.value) {
    const date = new Date(startDate.value)
    date.setMonth(date.getMonth() + 1)
    return date
  }
})
const { fetch, updateCapacity, availabilityResponse, days } = useAvailability(startDate, endDate)

const slots = computed(() =>
  sortArrayByKey(
    availabilityResponse.value?.availability_defined_default.availability_slots_defined || [],
    'hour_start',
  ),
)

function getDefaultCapacity(hourStart: number) {
  const defaultSlot =
    availabilityResponse.value?.availability_defined_default.availability_slots_defined.find(
      (s) => s.hour_start == hourStart,
    )
  if (!defaultSlot) {
    throw new Error('Default slot not found')
  }
  return defaultSlot?.capacity
}

function getDatedCapacity(date: Date, hourStart: number) {
  if (!availabilityResponse.value) throw new Error('Availability response is not defined')
  const datedCapacity = availabilityResponse.value?.availability_defined_dated.find(
    (s) => s.date == formatDate(date, 'yyyy-MM-dd'),
  )?.availability_slots_defined
  const datedSlot = datedCapacity?.find((s) => s.hour_start == hourStart)
  if (datedSlot) {
    return datedSlot.capacity
  } else {
    return getDefaultCapacity(hourStart)
  }
}

function handleCapacityUpdate(date: Date, slotHourStart: number, v: number) {
  updateCapacity(date, slotHourStart, v)
}

watch(startDate, fetch)
fetch()
</script>

<template>
  <Page :page-title="'Beschikbaarheid'">
    <IftaLabel>
      <DatePicker v-model="startDate" view="month" input-id="datepicker" :date-format="'MM yy'" />
      <label for="datepicker">Kies een maand</label>
    </IftaLabel>
    <table>
      <thead>
        <tr>
          <th></th>
          <th colspan="2">Aantal adviseurs per dagdeel</th>
        </tr>
        <tr>
          <th>Datum</th>
          <th v-for="s in slots" :key="s.hour_start">{{ s.hour_start }}u - {{ s.hour_end }}u</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in days" :key="d.toDateString()">
          <td>
            {{
              d.toLocaleDateString('nl-NL', {
                weekday: 'short',
                month: 'long',
                day: 'numeric',
                year: 'numeric',
              })
            }}
          </td>
          <td v-for="s in slots" :key="s.hour_start">
            <InputNumber
              :model-value="getDatedCapacity(d, s.hour_start) || 0"
              class="max-w-[150px]"
              size="small"
              inputId="horizontal-buttons"
              showButtons
              buttonLayout="horizontal"
              :step="1"
              :min="0"
              :max="100"
              :mode="'decimal'"
              fluid
              @update:model-value="(v: number) => handleCapacityUpdate(d, s.hour_start, v)"
            >
              <template #incrementicon>
                <span class="pi pi-plus" />
              </template>
              <template #decrementicon>
                <span class="pi pi-minus" />
              </template>
            </InputNumber>
          </td>
        </tr>
      </tbody>
    </table>
  </Page>
</template>
