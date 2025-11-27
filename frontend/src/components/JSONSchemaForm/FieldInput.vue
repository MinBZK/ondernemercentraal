<script setup lang="ts">
import Textarea from 'primevue/textarea'

const props = withDefaults(
  defineProps<{
    type?: 'text' | 'number'
    modelValue: string | number | null
    hasMissingRequiredValue: boolean
    placeholder: string
    fieldId: string
    readonly: boolean
    minimumValue?: number
    maximumValue?: number
  }>(),
  {
    type: 'text',
  },
)

const initialValue = computed(() => {
  if (typeof props.modelValue == 'number' || typeof props.modelValue == 'bigint') {
    return props.modelValue.toString()
  } else {
    return props.modelValue || ''
  }
})

// initialize
const input = ref<string | null>(null)
watch(initialValue, () => (input.value = initialValue.value), { immediate: true })

const parsedModelValue = computed(() => {
  if (props.type == 'text') {
    return input.value && typeof input.value == 'string' && input.value.length == 0
      ? ''
      : input.value
  } else if (input.value) {
    return parseInt(input.value)
  } else {
    return input.value
  }
})

const emit = defineEmits<{
  'update:model-value': [value: string | number | null]
}>()
watch(input, () => {
  const v = parsedModelValue.value
  // if there is no input (string with length 0), make the value null
  emit('update:model-value', typeof v === 'string' && v.length == 0 ? null : v)
})

const isValidNumber = computed(() => {
  const number = Number(input.value)
  return number >= (props.minimumValue || -Infinity) && number <= (props.maximumValue || Infinity)
})

const error = computed(() => {
  if (!isValidNumber.value && props.type == 'number') {
    return `De waarde mag niet kleiner zijn dan ${props.minimumValue || -Infinity} en niet groter dan ${props.maximumValue || Infinity}`
  }
})
</script>

<template>
  <Textarea
    v-if="type == 'text'"
    :id="fieldId"
    :placeholder="placeholder"
    v-model="input"
    :type="type"
    autocomplete="off"
    :class="['w-full', hasMissingRequiredValue && 'p-invalid']"
    :disabled="readonly"
  />

  <InputText
    v-else-if="type == 'number'"
    :id="fieldId"
    :placeholder="placeholder"
    v-model="input"
    :type="type"
    autocomplete="off"
    :class="['w-full', hasMissingRequiredValue && 'p-invalid']"
    :invalid="!isValidNumber"
    :disabled="readonly"
    :min="minimumValue"
    :max="maximumValue"
  />
  <span class="text-xs text-red-500">{{ error }}</span>
</template>
