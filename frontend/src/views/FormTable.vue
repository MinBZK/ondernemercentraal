<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

const trackId = ref()
const appointmentId = ref()
const requestId = ref()
const { forms, fetchMany: fetchManyForms } = useForms(trackId, appointmentId, requestId)
const { formLabels } = useEntityLabels()

fetchManyForms()

const formTableConfig: TableColumnConfig<components['schemas']['FormData']>[] = [
  {
    key: 'case_description',
    label: formLabels.case_description,
    dataType: 'text',
  },
  {
    key: 'form_template_name',
    label: formLabels.form_template_name,
    dataType: 'text',
  },
  {
    key: 'form_link_type',
    label: formLabels.form_link_type,
    dataType: 'custom',
  },
  {
    key: 'updated_at',
    label: formLabels.updated_at,
    dataType: 'datetime',
  },
  {
    key: 'status',
    label: formLabels.status,
    dataType: 'text',
  },
]

const selectedFormDataId = ref<string>()
const showForm = ref(false)

type FormLinkType = Exclude<components['schemas']['FormData']['form_link_type'], null>
const formLinkTypeMapping: Record<FormLinkType, string> = {
  appointment: 'Gesprek',
  request: 'Verzoek',
  track: 'Dossier',
}

function getLinkedRoute(formData: components['schemas']['FormData']) {
  const routeNames: Record<FormLinkType, FormDataViewRoutes> = {
    appointment: 'BeheerAppointmentFormData',
    request: 'BeheerRequestFormData',
    track: 'BeheerTrackFormData',
  }

  const {
    id: formDataId,
    case_id: caseId,
    request_id: requestId,
    appointment_id: appointmentId,
    track_id: trackId,
  } = formData

  return {
    name: routeNames[formData.form_link_type as FormLinkType],
    params: {
      formDataId,
      caseId,
      appointmentId,
      trackId,
      requestId,
    },
  }
}

function getRouteName(formData: components['schemas']['FormData']) {
  const routeNames: Record<FormLinkType, FormDataViewRoutes> = {
    appointment: 'BeheerAppointmentFormData',
    request: 'BeheerRequestFormData',
    track: 'BeheerTrackFormData',
  }

  return routeNames[formData.form_link_type as FormLinkType]
}
</script>

<template>
  <OcTable
    :data="forms"
    :table-config="formTableConfig"
    :id-key="'id'"
    show-action-column
    :row-link-config="{
      routeName: getRouteName,
      params: [
        {
          routeIdKey: 'formDataId',
          idKey: 'id',
        },
        {
          routeIdKey: 'appointmentId',
          idKey: 'appointment_id',
        },
        {
          routeIdKey: 'trackId',
          idKey: 'track_id',
        },
        {
          routeIdKey: 'requestId',
          idKey: 'request_id',
        },
        {
          routeIdKey: 'caseId',
          idKey: 'case_id',
        },
      ],
    }"
    v-if="forms.length > 0"
  >
    <template #custom="{ row: formData, column }">
      <span v-if="column.key === 'form_link_type' && formData.form_link_type">
        {{ formLinkTypeMapping[formData.form_link_type] }}
      </span>
    </template>
    <template #action="{ row: formData }">
      <router-link :to="getLinkedRoute(formData)">
        <Button
          :icon="PrimeIcons.ARROW_CIRCLE_RIGHT"
          size="small"
          :variant="'outlined'"
          :label="'Bekijk'"
        />
      </router-link>
    </template>
  </OcTable>
  <DialogForm :form-data-id="selectedFormDataId" @submit="fetchManyForms()" v-model="showForm" />
</template>
