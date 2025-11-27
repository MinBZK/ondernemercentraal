<script setup lang="ts">
import type { JSONSchema7Type } from 'json-schema'

const props = defineProps<{
  enumValues: JSONSchema7Type[]
  placeholder: string
  modelValue: string[] | null
  hasMissingRequiredValue: boolean
  fieldId: string
  readonly: boolean
}>()

const selectedValue = defineModel<JSONSchema7Type | null>({ default: null })

const modelValue = toRef(props, 'modelValue')
watch(
  modelValue,
  () => {
    selectedValue.value = modelValue.value
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <Select
    v-if="enumValues.length > 0"
    v-model="selectedValue"
    :input-id="fieldId"
    :options="enumValues"
    :placeholder="placeholder"
    :class="['w-full', hasMissingRequiredValue && 'p-invalid']"
    :disabled="readonly"
    show-clear
  />
</template>
