<script setup lang="ts">
import type {
  JSONSchemaDefinitions,
  JSONSchemaPayload,
  FieldValueTypes,
  GenesysField,
} from './types'
import FieldInput from './FieldInput.vue'
import FieldSelect from './FieldSelect.vue'
import FieldDate from './FieldDate.vue'
import FieldObject from './FieldObject.vue'
import FieldArray from './FieldArray.vue'
import FormField from './FormField.vue'
import { getPropertiesFromSchema } from '@/components/JSONSchemaForm/util'

const props = withDefaults(
  defineProps<{
    field: GenesysField
    definitions: JSONSchemaDefinitions | undefined
    fullWidth?: boolean
    hideLabel: boolean
    hasMissingValue: boolean
    readonly: boolean
    currentValue: FieldValueTypes
    isRequired: boolean
  }>(),
  {
    fullWidth: true,
  },
)

const currentValue = toRef(props, 'currentValue')

const referenceSchema = computed(() => jsonSchemaField.value.$ref)
const jsonSchemaField = computed(() => props.field.jsonSchemaField)
const fieldId = computed(() => props.field.fieldName.toLocaleLowerCase().replace(' ', '-'))

type ObjectFieldTypes = 'object-with-ref' | 'object-without-ref'

type FieldTypes =
  | 'input-string'
  | 'input-number'
  | 'select'
  | 'date'
  | 'array'
  | 'boolean'
  | undefined
  | ObjectFieldTypes

const isObject = computed(
  () =>
    jsonSchemaField.value.type == 'object' ||
    (referenceSchema.value !== undefined && jsonSchemaField.value.type !== 'array') ||
    Boolean(jsonSchemaField.value.allOf),
)

const isReadonly = computed(() => Boolean(jsonSchemaField.value.readOnly))

const fieldType = computed((): FieldTypes => {
  if (jsonSchemaField.value.enum !== undefined) {
    return 'select'
  } else if (jsonSchemaField.value.type == 'string' && jsonSchemaField.value.format === undefined) {
    return 'input-string'
  } else if (jsonSchemaField.value.type == 'string' && jsonSchemaField.value.format == 'date') {
    return 'date'
  } else if (jsonSchemaField.value.type == 'number' || jsonSchemaField.value.type == 'integer') {
    return 'input-number'
  } else if (jsonSchemaField.value.type == 'array') {
    return 'array'
  } else if (isObject.value && referenceSchema.value !== undefined) {
    return 'object-with-ref'
  } else if (isObject.value && referenceSchema.value === undefined) {
    return 'object-without-ref'
  } else if (jsonSchemaField.value.type == 'boolean') {
    return 'boolean'
  } else {
    return undefined
  }
})

// value
const emit = defineEmits<{
  updateValue: [value: FieldValueTypes]
  updateHasMissingValue: [valid: boolean]
}>()

const initialValueParsedInput = computed(() =>
  typeof currentValue.value == 'string' || typeof currentValue.value == 'number'
    ? currentValue.value
    : null,
)

const initialValueParsedSelect = computed(() =>
  typeof currentValue.value == 'string' ? currentValue.value : null,
)

const initialValueParsedDate = initialValueParsedSelect

const initialValueParsedObject = computed(() =>
  typeof currentValue.value == 'object' ? (currentValue.value as JSONSchemaPayload) : null,
)

const initialValueParsedArray = computed(() =>
  currentValue.value ? (currentValue.value as JSONSchemaPayload[]) : null,
)

const initialValueBoolean = computed(() =>
  typeof currentValue.value == 'boolean' ? Boolean(currentValue.value) : false,
)

// initialize models
const fieldValueInput = ref<string | number | null>(initialValueParsedInput.value)
const fieldValueSelect = ref<string | null>(initialValueParsedSelect.value)

const fieldValueDate = ref<string | null>(initialValueParsedDate.value)
const fieldValueObject = ref<JSONSchemaPayload | null>(initialValueParsedObject.value)
const fieldValueArray = ref<JSONSchemaPayload[] | null>(null)
const fieldValueBoolean = ref<boolean>(initialValueBoolean.value)

watch(initialValueParsedInput, () => (fieldValueInput.value = initialValueParsedInput.value), {
  immediate: true,
})
watch(initialValueParsedSelect, () => (fieldValueSelect.value = initialValueParsedSelect.value), {
  immediate: true,
})
watch(initialValueParsedDate, () => (fieldValueDate.value = initialValueParsedDate.value), {
  immediate: true,
})
watch(initialValueParsedObject, () => (fieldValueObject.value = initialValueParsedObject.value), {
  immediate: true,
})
watch(initialValueParsedArray, () => (fieldValueArray.value = initialValueParsedArray.value), {
  immediate: true,
})
watch(initialValueBoolean, () => (fieldValueBoolean.value = initialValueBoolean.value), {
  immediate: true,
})

// update payload
watch(fieldValueInput, () => emit('updateValue', fieldValueInput.value))
watch(fieldValueSelect, () => emit('updateValue', fieldValueSelect.value))
watch(fieldValueDate, () => emit('updateValue', fieldValueDate.value))
watch(fieldValueBoolean, () => emit('updateValue', fieldValueBoolean.value))
watch(fieldValueObject, () => emit('updateValue', fieldValueObject.value), { deep: true })
watch(fieldValueArray, () => emit('updateValue', fieldValueArray.value), { deep: true })

const hasMissingRequiredValue = computed(() => props.hasMissingValue && props.isRequired)
</script>

<template>
  <template v-if="isReadonly">
    <MarkdownText :text="field.fieldName" class="my-4" />
  </template>
  <template v-else>
    <FormField
      :label="field.fieldName"
      :label-font-size="isObject ? 'large' : 'small'"
      :field-id="fieldId"
      :is-required="isRequired"
      :full-width="fieldType == 'input-string' || fieldType == 'object-without-ref'"
      :warning="
        hasMissingRequiredValue && fieldType !== 'array'
          ? isObject
            ? 'Bevat missende waardes voor verplichte velden'
            : 'Verplicht'
          : undefined
      "
      :hide-label="hideLabel"
      :expandable="isObject"
    >
      <FieldInput
        v-if="fieldType == 'input-string' || fieldType == 'input-number'"
        v-model="fieldValueInput"
        :has-missing-required-value="hasMissingRequiredValue"
        :placeholder="field.fieldName"
        :type="fieldType == 'input-number' ? 'number' : 'text'"
        :field-id="fieldId"
        :readonly="readonly"
        :minimum-value="jsonSchemaField.minimum"
        :maximum-value="jsonSchemaField.maximum"
      />

      <FieldSelect
        v-if="fieldType == 'select'"
        v-model="fieldValueSelect"
        :enum-values="jsonSchemaField.enum || []"
        :placeholder="`Selecteer ${field.fieldName}`"
        :has-missing-required-value="hasMissingRequiredValue"
        :field-id="fieldId"
        :readonly="readonly"
      />

      <FieldDate
        v-if="fieldType == 'date'"
        v-model="fieldValueDate"
        :has-missing-required-value="hasMissingRequiredValue"
        :placeholder="`Kies ${field.fieldName}`"
        :field-id="fieldId"
        :readonly="readonly"
      />

      <FieldObject
        v-if="isObject"
        v-model="fieldValueObject"
        :field-name="field.fieldName"
        :schema="getPropertiesFromSchema(field, definitions)"
        :definitions="definitions"
        :required="isRequired"
        :has-missing-required-value="hasMissingRequiredValue"
        :readonly="readonly"
        :show-content="true"
      />
      <FieldArray
        v-if="fieldType == 'array'"
        v-model="fieldValueArray"
        :field="field"
        :definitions="definitions"
        :schema="getPropertiesFromSchema(field, definitions)"
        :readonly="readonly"
      />

      <FormBoolean
        v-if="fieldType == 'boolean'"
        v-model="fieldValueBoolean"
        :readonly="readonly"
        :has-missing-required-value="hasMissingRequiredValue"
      />
      <span v-if="fieldType === undefined"
        >No field type defined for {{ field.fieldName }}. JSON Schema definition:
        <pre>{{ jsonSchemaField }}</pre>
      </span>
    </FormField>
  </template>
</template>
