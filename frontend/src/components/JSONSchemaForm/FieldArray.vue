<script setup lang="ts">
import type { FieldValueTypes, GenesysField, JSONSchemaDefinitions } from './types'
import { PrimeIcons } from '@primevue/core/api'
import JSONSchemaForm from './Form.vue'
import type { JSONSchemaPayload } from './types'
import type { JSONSchema7 } from 'json-schema'
import Field from './Field.vue'

const props = defineProps<{
  field: GenesysField
  definitions?: JSONSchemaDefinitions
  schema?: JSONSchema7
  modelValue: JSONSchemaPayload[] | null
  readonly: boolean
}>()

const itemField = computed((): GenesysField | null =>
  typeof props.field.jsonSchemaField.items == 'object'
    ? {
        jsonSchemaField: props.field.jsonSchemaField.items as JSONSchema7,
        fieldName: props.field.fieldName,
        isChild: false,
      }
    : null,
)

const showDialog = ref<boolean>(false)

const items = defineModel<JSONSchemaPayload[] | null>({ default: null })

const selectedIndex = ref<number | null>(null)

function addItem() {
  if (!items.value) {
    items.value = [{}]
  } else {
    items.value.push({})
  }
  selectedIndex.value = !items.value ? 0 : items.value.length - 1
}

function removeItem(index: number) {
  if (items.value) items.value.splice(index, 1)
  delete validity.value[index]
}

function updateItem(index: number, value: FieldValueTypes) {
  if (value === null) {
    removeItem(index)
  } else {
    // hacky way to deal with recursive types
    const v = value as JSONSchemaPayload
    if (items.value) items.value[index] = v
  }
}

const emit = defineEmits<{
  'update:has-missing-value': [v: boolean]
}>()

watch(
  items,
  () => {
    if ((items.value && items.value.length == 0) || !items.value) selectedIndex.value = null
  },
  { deep: true },
)

const modelValue = toRef(props, 'modelValue')
watch(
  modelValue,
  () => {
    items.value = modelValue.value
  },
  {
    immediate: true,
  },
)

const validity = ref<Record<number, boolean>>({})
const isValid = computed(() => Object.values(validity.value).every((v) => v))
watch(isValid, () => emit('update:has-missing-value', !isValid.value))
</script>

<template>
  <div class="w-full">
    <template v-if="itemField && items">
      <Field
        v-for="(item, index) in items"
        class="mb-2"
        :key="index"
        :readonly="readonly"
        :field="itemField"
        :is-required="false"
        :definitions="definitions"
        :current-value="item"
        :hide-label="true"
        :has-missing-value="false"
        :show-divider="false"
        @update-value="(v) => updateItem(index, v)"
        @update-has-missing-value="(v) => (validity[index] = v)"
      />
    </template>

    <Button label="Toevoegen" :icon="PrimeIcons.PLUS" @click="addItem()" :disabled="readonly" />

    <Dialog
      :key="itemField?.fieldName"
      v-model:visible="showDialog"
      modal
      :header="itemField?.fieldName"
      :style="{ width: '50rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      :dismissable-mask="true"
    >
      <JSONSchemaForm
        v-if="definitions && schema && selectedIndex !== null && items"
        v-model="items[selectedIndex]"
        :json-schema="{ ...schema, ...definitions }"
        :readonly="readonly"
      />
    </Dialog>
  </div>
</template>

<style scoped>
ul {
  list-style-type: none;
}

table {
  border-collapse: collapse;
  margin-bottom: 1em;
}

th {
  text-align: left;
}

td {
  padding-right: 0.5em;
  padding-bottom: 0.75em;
}
</style>
