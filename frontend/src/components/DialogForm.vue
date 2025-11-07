<script setup lang="ts">
import type { components } from '@/api/schema'
type formTemplateName = components['schemas']['FormTemplate']['name']

const props = defineProps<{
  formTemplateName?: formTemplateName
  trackId?: string
  appointmentId?: string
  requestId?: string
  formDataId?: string
}>()

const formTemplateName = toRef(props, 'formTemplateName')

function paginatedRequired(formTemplateName: formTemplateName) {
  const paginatedForms: formTemplateName[] = [
    'BBZ-aanvraag',
    'BBZ-verlenging-aanvraag',
    'IOAZ-aanvraag',
  ]
  return paginatedForms.includes(formTemplateName)
}

const trackId = toRef(props, 'trackId')
const appointmentId = toRef(props, 'appointmentId')
const requestId = toRef(props, 'requestId')

const { updateForm, createForm } = useForms(trackId, appointmentId, requestId)
const formDataId = toRef(props, 'formDataId')
const { formData, fetch, editAllowed, formPayload, initialized } = useFormData(formDataId)
const { notify } = useNotification()

watch(
  formDataId,
  () => {
    if (formDataId.value) {
      fetch()
    }
  },
  { immediate: true },
)

const emit = defineEmits<{
  update: []
}>()

async function handleSaveForm(formDataUpsert: components['schemas']['FormDataUpsert']) {
  if (formDataId.value) {
    await updateForm(formDataId.value, formDataUpsert)
  } else {
    if (!formTemplateName.value) {
      throw new Error('Formulier template naam is vereist om een nieuw formulier aan te maken')
    }
    const { data: formDataCreated } = await createForm(formTemplateName.value, formDataUpsert)
    if (!formDataCreated) {
      throw new Error('Formulier kon niet worden aangemaakt')
    }
    formDataId.value = formDataCreated.id
  }
  emit('update')
}

async function saveFormData(showNotification: boolean = true) {
  await handleSaveForm({
    payload: formPayload.value || null,
  })
  if (showNotification) {
    notify({
      message: 'Het formulier is opgeslagen',
      severity: 'success',
    })
  }
  fetch()
}

const validation = ref<components['schemas']['PayloadValidation']>()
const formTemplateNameFinal = computed(() => {
  return props.formTemplateName || formData.value?.form_template_name
})
</script>

<template>
  <DialogCrud
    v-if="formTemplateNameFinal"
    :header="formTemplateNameFinal"
    :use-wide-mode="paginatedRequired(formTemplateNameFinal)"
    :dismissable-mask="false"
  >
    <template #default>
      <FormDataCrud
        v-if="initialized"
        v-model:form-payload="formPayload"
        v-model:validation="validation"
        :form-template-name="formTemplateNameFinal"
        :edit-allowed="editAllowed"
        @update-page="saveFormData(false)"
        :apply-pagination="paginatedRequired(formTemplateNameFinal)"
      />
    </template>
    <template #actions>
      <FormDataActions
        v-model:validation="validation"
        :edit-allowed="editAllowed"
        :form-data="formData"
        :appointment-id="appointmentId"
        :request-id="requestId"
        :track-id="trackId"
        :form-template-name="formTemplateNameFinal"
        @saved="saveFormData()"
        @status-updated="fetch()"
      />
    </template>
  </DialogCrud>
</template>
