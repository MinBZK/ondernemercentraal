<script setup lang="ts">
import type { JSONSchema7 } from 'json-schema'
import type { JSONSchemaDefinitions } from './types'
import type { JSONSchemaPayload } from './types'
import JSONSchemaForm from './Form.vue'

const props = withDefaults(
  defineProps<{
    fieldName: string
    definitions?: JSONSchemaDefinitions
    schema?: JSONSchema7
    required: boolean
    hasMissingRequiredValue: boolean
    readonly: boolean
    hideFields?: boolean
    showContent?: boolean
  }>(),
  {
    hideFields: false,
    showContent: true,
  },
)

const visible = ref<boolean>(false)
const childSchema = computed(() => {
  return { ...props.schema, definitions: props.definitions }
})

const payload = defineModel<JSONSchemaPayload | null>({ required: true })
</script>

<template>
  <div class="grid grid-cols-1 w-full gap-4 mb-4">
    <JSONSchemaForm
      v-if="childSchema && showContent"
      v-model="payload"
      :json-schema="childSchema"
      :readonly="readonly"
    />
  </div>

  <Dialog
    v-model:visible="visible"
    modal
    :header="fieldName"
    :style="{ width: '50rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    :dismissable-mask="true"
  >
    <div class="mt-1">
      <JSONSchemaForm
        v-if="childSchema && payload"
        v-model="payload"
        :json-schema="childSchema"
        :readonly="readonly"
      />
    </div>
  </Dialog>
</template>

<style scoped>
.dialog {
  width: '50rem';
}
</style>
