<script setup lang="ts">
import { parseISO, format, isValid } from 'date-fns'

const props = defineProps<{
  modelValue: string | null
  hasMissingRequiredValue: boolean
  fieldId: string
  readonly: boolean
}>()

const parseDateToString = (d: Date) => (d ? format(d, 'yyyy-MM-dd') : null)
const parseStringToDate = (s: string) => {
  const date = s ? parseISO(s) : null
  return isValid(date) ? date : null
}

const date = ref<Date | null>(null)
const dateString = defineModel<string | null>({ default: null })

const modelValue = toRef(props, 'modelValue')
watch(
  modelValue,
  () => (date.value = modelValue.value ? parseStringToDate(modelValue.value) : null),
  { immediate: true },
)
watch(date, () => (dateString.value = date.value ? parseDateToString(date.value) : null))
</script>

<template>
  <DatePicker
    v-model="date"
    :class="['w-full', hasMissingRequiredValue && 'p-invalid']"
    date-format="d MM yy"
    :input-id="fieldId"
    :disabled="readonly"
  />
</template>
