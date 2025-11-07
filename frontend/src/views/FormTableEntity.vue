<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

type FormName = components['schemas']['FormTemplate']['name']
type RequiredFormTemplate = components['schemas']['RequiredFormTemplate']

const props = defineProps<{
  requiredForms: RequiredFormTemplate[]
  trackId?: string
  appointmentId?: string
  requestId?: string
  caseId?: string
}>()

const { formLabels } = useEntityLabels()

const trackId = toRef(props, 'trackId')
const appointmentId = toRef(props, 'appointmentId')
const requestId = toRef(props, 'requestId')

const { forms, fetchMany: fetchManyForms } = useForms(trackId, appointmentId, requestId)

fetchManyForms()

const formTableConfig: TableColumnConfig<components['schemas']['FormData']>[] = [
  {
    key: 'form_template_name',
    label: formLabels.form_template_name,
    dataType: 'text',
  },
  {
    key: 'has_valid_payload',
    label: formLabels.has_valid_payload,
    dataType: 'boolean',
  },
  {
    key: 'created_at',
    label: formLabels.created_at,
    dataType: 'datetime',
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

const { me } = useAuth()

const missingForms = computed(() =>
  props.requiredForms.filter(
    (f) =>
      !forms.value.some((form) => form.form_template_name === f.name) &&
      me.value?.permissions.includes(f.required_permission),
  ),
)

const formTemplateName = ref<FormName>()
const selectedFormData = ref<components['schemas']['FormData']>()
const showFormCrud = defineModel<boolean>('showFormCrud', { default: false })
const route = useRoute()
const routeName = computed(() => route.name)
watch(routeName, (newRouteName, oldRouteName) => {
  if (newRouteName !== oldRouteName) {
    fetchManyForms()
  }
})

type FormTemplateName = components['schemas']['FormTemplate']['name']

function getFormRoute(formTemplateName: FormTemplateName) {
  const targetRouteName: FormDataCreateRoutes = appointmentId.value
    ? 'BeheerAppointmentFormCreate'
    : 'BeheerTrackFormCreate'

  const targetRoute = {
    name: targetRouteName,
    params: {
      formTemplateName: formTemplateName,
      caseId: props.caseId,
    },
  }

  if (appointmentId.value) {
    Object.assign(targetRoute.params, { appointmentId: appointmentId.value })
  } else if (trackId.value) {
    Object.assign(targetRoute.params, { trackId: trackId.value })
  }

  return targetRoute
}
</script>

<template>
  <template v-if="missingForms.length > 0">
    <h3 class="my-4">Nog niet ingevulde formulieren</h3>
    <table>
      <thead>
        <tr>
          <th>Formulier</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="form in missingForms" :key="form.name">
          <td>{{ form.name }}</td>
          <td>
            <router-link :to="getFormRoute(form.name)">
              <Button
                :icon="PrimeIcons.FILE_EDIT"
                size="small"
                :variant="'outlined'"
                :label="'Invullen'"
              />
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </template>

  <h3 class="my-4" v-if="forms.length > 0">Ingevulde formulieren</h3>
  <OcTable
    :data="forms"
    :table-config="formTableConfig"
    :id-key="'id'"
    show-action-column
    v-if="forms.length > 0"
    ><template #action="{ row: form }">
      <router-link
        :to="{
          name: appointmentId ? 'BeheerAppointmentFormData' : 'BeheerTrackFormData',
          params: {
            formDataId: form.id,
          },
        }"
      >
        <Button
          :icon="PrimeIcons.ARROW_CIRCLE_RIGHT"
          size="small"
          :variant="'outlined'"
          :label="'Bekijk'"
          @click="[
            (selectedFormData = form),
            (formTemplateName = form.form_template_name),
            (showFormCrud = true),
          ]"
        />
      </router-link>
    </template>
  </OcTable>

  <router-view name="nestedForm" />
</template>
