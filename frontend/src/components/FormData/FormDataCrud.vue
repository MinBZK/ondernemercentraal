<script lang="ts" setup>
import type { components } from '@/api/schema'
import JSONSchemaForm from '@/components/JSONSchemaForm/Form.vue'
import type { JSONSchemaPayload } from '../JSONSchemaForm/types'

const props = defineProps<{
  formTemplateName: components['schemas']['FormTemplate']['name']
  editAllowed: boolean
  applyPagination: boolean
}>()

const formPayload = defineModel<JSONSchemaPayload>('formPayload', { required: false })

const formTemplateName = toRef(props, 'formTemplateName')
const { schema, fetch: fetchSchema } = useFormTemplate(formTemplateName)
fetchSchema()

const validation = defineModel<components['schemas']['PayloadValidation']>('validation', {
  required: false,
})

function handlePagination() {
  const dialogContainerDiv = document.getElementById('dialog-content-container')
  if (!dialogContainerDiv) throw new Error('Dialog content container not found')
  dialogContainerDiv.scrollTop = 0
  emit('updatePage')
}

const emit = defineEmits<{
  updatePage: []
}>()

watch(formTemplateName, fetchSchema, { immediate: true })
</script>

<template>
  <JSONSchemaForm
    v-if="schema"
    @update:validation="(v) => (validation = v)"
    v-model="formPayload"
    :json-schema="schema"
    :readonly="!editAllowed"
    :apply-pagination="applyPagination"
    @update:selected-field="handlePagination()"
  />
</template>
