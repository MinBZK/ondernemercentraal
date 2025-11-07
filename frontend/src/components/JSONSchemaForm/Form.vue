<script setup lang="ts">
import type { JSONSchema7 } from 'json-schema'
import type { FieldValueTypes, GenesysField, JSONSchemaPayload } from './types'
import Field from './Field.vue'
import { useJsonSchemaForm } from './composables/useJsonSchemaForm'
import { PrimeIcons } from '@primevue/core/api'
import type { components } from '@/api/schema'

const props = withDefaults(
  defineProps<{
    jsonSchema: JSONSchema7
    fullWidth?: boolean
    readonly?: boolean
    applyPagination?: boolean
  }>(),
  {
    fullWidth: false,
    readonly: false,
    applyPagination: false,
  },
)

const payload = defineModel<JSONSchemaPayload | null>({ default: null })
const { validation } = useJsonSchemaValidation(props.jsonSchema, payload)
const { fields, paginationPossible } = useJsonSchemaForm(props.jsonSchema)

const emit = defineEmits<{
  'update:selectedField': [field: GenesysField]
  'update:validation': [validation: components['schemas']['PayloadValidation']]
}>()

watch(
  validation,
  () => {
    if (validation.value) {
      emit('update:validation', validation.value)
    }
  },
  { deep: true },
)

function updatePayload(fieldName: string, v: FieldValueTypes) {
  let newPayload = { ...payload.value }

  if (v === null && payload.value) {
    delete newPayload[fieldName]
  } else if (payload.value) {
    newPayload[fieldName] = v
  } else {
    newPayload = { [fieldName]: v }
  }

  if (payload.value) {
    const payloadHasChanged = JSON.stringify(newPayload) !== JSON.stringify(payload.value)
    if (payloadHasChanged) payload.value = JSON.parse(JSON.stringify(newPayload)) // Ensure reactivity
  } else {
    payload.value = newPayload
  }
}

const paginationPossibleAndRequired = computed(() => {
  const possibleAndRequired = paginationPossible.value && props.applyPagination
  if (props.applyPagination && !paginationPossible.value) {
    console.error('Pagination is only possible for object fields.', fields)
  }
  return possibleAndRequired
})

const selectedField = ref<GenesysField>(fields[0])

function fieldIsRequired(field: GenesysField) {
  return validation.value?.required_properties.includes(field.fieldName)
}

const visibleFields = computed(() => {
  const fieldsInPage = fields.filter(
    (f) => f.fieldName === selectedField.value.fieldName || !paginationPossibleAndRequired.value,
  )

  return fieldsInPage.filter((f) => {
    // check whether the field is a child field that is now required based on the validation.
    const isRequired = fieldIsRequired(f)
    const isNotRequiredChild = f.isChild && !isRequired
    const showField = !isNotRequiredChild
    return showField
  })
})

const nextField = computed(() => {
  const currentIndex = fields.findIndex((f) => f.fieldName === selectedField.value.fieldName)
  return fields[currentIndex + 1] || null
})

const previousField = computed(() => {
  const currentIndex = fields.findIndex((f) => f.fieldName === selectedField.value.fieldName)
  return fields[currentIndex - 1] || null
})

watch(selectedField, () => {
  emit('update:selectedField', selectedField.value)
})

const payloadValueIsMissing = (field: GenesysField) => {
  const value = payload.value?.[field.fieldName]
  return value === null || value === undefined
}

function getCurrentValue(f: GenesysField) {
  return payload.value && payload.value[f.fieldName] ? payload.value[f.fieldName] : null
}
</script>

<template>
  <div
    :class="[
      'grid',
      paginationPossibleAndRequired ? 'grid-cols-[80%_20%] gap-x-6 ' : 'grid-cols-1',
    ]"
  >
    <div class="flex-row overflow-x-auto">
      <Field
        v-for="f in visibleFields"
        :key="f.fieldName"
        :is-required="Boolean(validation?.required_properties.includes(f.fieldName))"
        :field="f"
        :has-missing-value="payloadValueIsMissing(f)"
        :definitions="jsonSchema.definitions || jsonSchema.$defs"
        :payload="payload || undefined"
        :current-value="getCurrentValue(f)"
        :hide-label="false"
        :readonly="readonly"
        @update-value="(v) => updatePayload(f.fieldName, v)"
      />
      <ValidationErrors
        v-if="validation && !paginationPossibleAndRequired"
        :validation="validation"
      />
      <div class="flex gap-x-2">
        <Button
          v-if="paginationPossibleAndRequired && previousField"
          :icon="PrimeIcons.CHEVRON_LEFT"
          :label="previousField.fieldName"
          @click="selectedField = previousField"
          :variant="'outlined'"
        />
        <Button
          v-if="paginationPossibleAndRequired && nextField"
          :icon="PrimeIcons.CHEVRON_RIGHT"
          :label="nextField.fieldName"
          @click="selectedField = nextField"
          :variant="'outlined'"
        />
      </div>
    </div>
    <div v-if="paginationPossibleAndRequired">
      <div class="sticky top-0 relative">
        <ul>
          <li v-for="f in fields" :key="f.fieldName" class="my-2">
            <a
              class="cursor-pointer"
              @click="selectedField = f"
              :class="selectedField.fieldName == f.fieldName ? 'font-bold' : ''"
              >{{ f.fieldName }}</a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
