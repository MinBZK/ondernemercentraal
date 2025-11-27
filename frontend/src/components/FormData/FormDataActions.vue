<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'

import type { components } from '@/api/schema'

const props = defineProps<{
  editAllowed: boolean
  formData?: components['schemas']['FormData']
  trackId?: string
  appointmentId?: string
  requestId?: string
  formTemplateName: components['schemas']['FormTemplate']['name']
}>()

const validation = defineModel<components['schemas']['PayloadValidation']>('validation', {
  required: false,
})

const trackId = toRef(props, 'trackId')
const appointmentId = toRef(props, 'appointmentId')
const requestId = toRef(props, 'requestId')
const formDataId = computed(() => props.formData?.id)

// const { notify } = useNotification()
const { me } = useAuth()

const { fetchMany } = useForms(trackId, appointmentId, requestId)
const { notify } = useNotification()
const { updateFormStatus } = useFormData(formDataId)

const emit = defineEmits<{
  statusUpdated: []
  saved: []
}>()

async function setApprovalStatus(targetStatus: components['schemas']['FormData']['status']) {
  await updateFormStatus(targetStatus)
  emit('statusUpdated')
  fetchMany()
  notify({
    message: `De status van het formulier is gewijzigd naar '${targetStatus}'`,
    severity: 'success',
  })
}
</script>

<template>
  <span v-if="!editAllowed">
    <Message class="mb-4 text-left"
      >Dit formulier heeft status {{ formData?.status }} en kan daarom niet meer aangepast
      worden.</Message
    >
  </span>
  <ValidationErrors :validation="validation" v-if="validation" />
  <div class="flex justify-end gap-x-2">
    <Button
      v-if="formData && !me?.permissions.includes('form:approve')"
      :icon="PrimeIcons.CHECK_CIRCLE"
      :label="formData.submitted ? 'Indienen ongedaan maken' : 'Ter goedkeuring indienen'"
      :disabled="!validation?.is_valid"
      :variant="'outlined'"
      @click="setApprovalStatus(formData?.submitted ? 'Gestart' : 'Ingediend')"
    />

    <Button
      v-if="formData && me?.permissions.includes('form:approve')"
      :label="formData.approved ? 'Goedkeuring intrekken' : 'Goedkeuren'"
      :disabled="!validation?.is_valid"
      :variant="'outlined'"
      @click="setApprovalStatus(formData?.approved ? 'Gestart' : 'Goedgekeurd')"
    />

    <Button
      @click="emit('saved')"
      :disabled="!editAllowed"
      label="Opslaan"
      :icon="PrimeIcons.SAVE"
    />
  </div>
</template>
