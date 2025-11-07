<script setup lang="ts">
import type { components } from '@/api/schema'
import type { FileUploadBeforeUploadEvent, FileUploadErrorEvent } from 'primevue/fileupload'

const props = defineProps<{
  fileType: components['schemas']['FileBase']['file_type']
  caseId?: string
  trackId?: string
  appointmentId?: string
}>()

const { baseUrl, token } = useApiClient()

const uploadUrl = computed(() => {
  const uploadBaseUrl = `${baseUrl}/api/file/?file_type=${props.fileType}&`
  if (props.caseId) {
    return `${uploadBaseUrl}case_id=${props.caseId}`
  } else if (props.trackId) {
    return `${uploadBaseUrl}track_id=${props.trackId}`
  } else if (props.appointmentId) {
    return `${uploadBaseUrl}appointment_id=${props.appointmentId}`
  } else {
    throw new Error('Either caseId, appointmentId or trackId must be provided')
  }
})

const { notify } = useNotification()

const emit = defineEmits<{
  uploadCompleted: []
}>()

// function handleUpload(event: FileUploadUploadEvent) {
function handleUpload() {
  // const response = JSON.parse(event.xhr.response)
  emit('uploadCompleted')
}

function handleUploadError(e: FileUploadErrorEvent) {
  notify({
    message: e['xhr']['responseText'],
    severity: 'error',
  })
}

function setHeaders(request: FileUploadBeforeUploadEvent) {
  request.xhr.open('POST', uploadUrl.value)
  request.xhr.setRequestHeader('Authorization', 'Bearer ' + token.value)
}
</script>

<template>
  <FileUpload
    mode="basic"
    name="file"
    :auto="true"
    :choose-label="'Kies bestand'"
    :choose-button-props="{
      size: 'small',
      variant: 'outlined',
    }"
    :url="uploadUrl"
    accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .jpg, .jpeg, .png"
    @upload="handleUpload"
    @before-send="setHeaders"
    @error="handleUploadError"
  >
  </FileUpload>
</template>
