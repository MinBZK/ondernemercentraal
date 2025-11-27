<script setup lang="ts" generic="T extends Record<string, any>, Y extends T">
import { getFormValues } from '@/util'

const props = withDefaults(
  defineProps<{
    formFieldConfig: FormField<T>[]
    data?: Y
    nColumns?: number
  }>(),
  {
    nColumns: 2,
  },
)

const emit = defineEmits<{
  updateState: [StatePayload]
}>()
const formState = reactive<FormState>({})

function getStateValidity() {
  const requiredFields = props.formFieldConfig.filter((f) => !f.optional)
  const invalidFields = requiredFields.filter((f) => {
    const valueObject = formState[f.key.toString()]
    const rawValue = valueObject?.value
    const rawValueIsEmpty = rawValue === undefined || rawValue === null || rawValue === ''
    return rawValueIsEmpty && !f.optional && !f.hide && f.type !== 'custom'
  })

  return invalidFields.length === 0
}

watch(
  formState,
  () => {
    const formValues = getFormValues<keyof FormState>(formState)
    emit('updateState', {
      formStateValues: formValues,
      isValid: getStateValidity(),
    })
  },
  { deep: true, immediate: true },
)

function splitArray<T>(items: T[], maxItemsPerArray: number): T[][] {
  if (maxItemsPerArray <= 0) {
    throw new Error('Y must be greater than 0')
  }

  const splittedArray: T[][] = []
  for (let i = 0; i < items.length; i += maxItemsPerArray) {
    splittedArray.push(items.slice(i, i + maxItemsPerArray))
  }
  return splittedArray
}

const fieldsPerColumn = computed(() =>
  splitArray(
    props.formFieldConfig.filter((f) => !f.hide),
    props.nColumns,
  ),
)

function mutateState(mutation: { key: string; value: FormFieldState | undefined }) {
  const { key, value } = mutation
  formState[key] = value
}

defineExpose({
  mutateState,
})
</script>

<template>
  <div
    v-for="(fields, index) in fieldsPerColumn"
    :key="index"
    :class="['grid gap-4 gap-4 mb-4', fields.length > 1 ? 'grid-cols-2' : 'grid-cols-1']"
  >
    <template v-for="fieldConfig in fields" :key="fieldConfig.key">
      <FormFieldCore
        v-if="fieldConfig.type !== 'custom'"
        :field="fieldConfig"
        @update-state="
          (v) => {
            formState[fieldConfig.key.toString()] = v
          }
        "
        :current-value="data?.[fieldConfig.key.toString()] || fieldConfig.defaultValue"
      />
      <slot name="after" v-bind="{ field: fieldConfig }" />
    </template>
  </div>
</template>
