<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { z } from 'zod'
import AppointmentSlotPicker from './AppointmentSlotPicker.vue'
import { getFormValues } from '@/util'
import { PrimeIcons } from '@primevue/core/api'

type Appointment = components['schemas']['Appointment']
type TabNames = 'Gesprek' | 'Formulieren' | 'Bestanden' | 'Gekoppeld traject' | 'Notities'

const props = withDefaults(
  defineProps<{
    caseId?: string
    appointmentId?: string
    tabName?: TabNames
  }>(),
  {
    tabName: 'Gesprek',
  },
)

const { appointmentLabels } = useEntityLabels()
const appointmentId = toRef(props, 'appointmentId')
const {
  createAppointment,
  updateAppointment,
  appointment,
  fetch: fetchAppointment,
} = useAppointment(appointmentId)
const { trackValues, fetch: fetchValues } = useTrackValue()
fetchValues()
fetchAppointment()

const appointmentTypeOptions: Appointment['appointment_type_name'][] = [
  'Checkgesprek',
  'Toekomstgesprek',
  'SHVO intake',
]

const statusOptions: Appointment['status'][] = ['Open', 'Voltooid', 'Geannuleerd']

const AppointmentNewSchema = schemas.AppointmentNew.strict()
type AppointmentNew = z.infer<typeof AppointmentNewSchema>

const appointmentState: Record<keyof AppointmentNew, FormFieldState | undefined> = reactive({
  appointment_type_name: undefined,
  start_time: undefined,
  end_time: undefined,
  partner_organization_name: undefined,
  status: undefined,
})

const { navigateToParentRoute } = useParentRoute()

async function handleSubmit() {
  if (props.appointmentId) {
    await updateAppointment(props.appointmentId, parsedAppointment.value)
  } else {
    if (!props.caseId) {
      throw new Error('No case id provided')
    }
    await createAppointment(props.caseId, parsedAppointment.value)
  }

  selectedAppointmentSlot.value = undefined
  navigateToParentRoute()
}

type AppointmentSlot = components['schemas']['AppintmentSlotWithAvailability']

const initialAppointmentSlot = ref<AppointmentSlot>()
const selectedAppointmentSlot = ref<AppointmentSlot>()

watch(
  appointment,
  () => {
    initialAppointmentSlot.value =
      appointment.value?.start_time && appointment.value?.end_time
        ? {
            start_time: appointment.value.start_time,
            end_time: appointment.value.end_time,
            has_advisor_available: true,
          }
        : undefined
    if (!selectedAppointmentSlot.value) {
      selectedAppointmentSlot.value = initialAppointmentSlot.value
    }
  },
  {
    immediate: true,
  },
)

const formValid = computed(() => {
  const partnerOrgMissing =
    selectedAppointmentType.value == 'Toekomstgesprek' &&
    !appointmentState.partner_organization_name?.valid
  return Boolean(appointmentState.appointment_type_name?.valid) && !partnerOrgMissing
})

const parsedAppointment = computed(() => {
  const formValues = getFormValues<keyof AppointmentNew>(appointmentState)
  return AppointmentNewSchema.parse(formValues)
})

watch(
  selectedAppointmentSlot,
  () => {
    appointmentState.start_time = {
      value: selectedAppointmentSlot.value?.start_time,
      errors: [],
      touched: true,
      valid: true,
    }
    appointmentState.end_time = {
      value: selectedAppointmentSlot.value?.end_time,
      errors: [],
      touched: true,
      valid: true,
    }
  },
  {
    immediate: true,
  },
)

const selectedAppointmentType = computed(() => {
  // returns a typed version of the selected appointment type
  return appointmentState.appointment_type_name?.value as Appointment['appointment_type_name']
})

watch(selectedAppointmentType, (newValue) => {
  if (newValue === 'Checkgesprek') {
    appointmentState.partner_organization_name = {
      value: undefined,
      errors: [],
      touched: false,
      valid: false,
    }
  }
})

const showAppointmentFormCrud = ref(false)
const showTrackCrud = ref(false)

// const { me } = useAuth()
const userCanEdit = computed(() => {
  return true
  // return me.value?.permissions.includes('appointment:update')
})

const requiredProductName: components['schemas']['AppConfig']['required_products'][0] =
  'Toekomstgesprek'

type TabIndices = '0' | '1' | '2' | '3' | '4'

const tabMapping: Record<TabNames, TabIndices> = {
  Gesprek: '0',
  Formulieren: '1',
  Bestanden: '2',
  'Gekoppeld traject': '3',
  Notities: '4',
}

const tabValueTest = ref<TabIndices>(tabMapping[props.tabName])

const { me } = useAuth()
</script>

<template>
  <DialogCrud header="Gesprek">
    <Tabs v-model:value="tabValueTest">
      <TabList>
        <Tab value="0">Gesprek </Tab>
        <Tab value="1" v-if="appointment && appointment.required_forms.length > 0">Formulieren</Tab>
        <Tab value="2" v-if="appointment">Bestanden</Tab>
        <Tab value="3" v-if="appointment && appointment.track">Gekoppeld traject</Tab>
        <Tab value="4" v-if="appointment && me?.permissions.includes('comment:read')">Notities</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <FormFieldCore
            :field="{
              key: 'appointment_type_name',
              label: appointmentLabels.appointment_type_name,
              type: 'select',
              options: appointmentTypeOptions,
              optional: false,
              readOnly: !userCanEdit,
            }"
            :initialize-select="true"
            @update-state="(v) => (appointmentState['appointment_type_name'] = v)"
            :current-value="appointment?.appointment_type_name"
          />

          <FormFieldCore
            v-if="selectedAppointmentType == 'Toekomstgesprek'"
            :field="{
              key: 'partner_organization',
              label: appointmentLabels.partner_organization_name,
              type: 'select',
              options: (
                trackValues?.partner_organization
                  .filter((p) => p.product_names.includes(requiredProductName))
                  .map((p) => p.name) || []
              ).sort(),
              optional: false,
              readOnly: !userCanEdit,
            }"
            :initialize-select="true"
            @update-state="
              (v) => {
                appointmentState['partner_organization_name'] = v
              }
            "
            :current-value="appointment?.partner_organization_name"
            class="mt-4"
          />

          <FormFieldCore
            :field="{
              key: 'status',
              label: appointmentLabels.status,
              type: 'select',
              options: statusOptions.sort(),
              optional: false,
              readOnly: !userCanEdit,
            }"
            @update-state="
              (v) => {
                appointmentState['status'] = v
              }
            "
            :current-value="appointment?.status || 'Open'"
            class="mt-4"
          />

          <h2 class="mt-4">Tijdslot</h2>

          <AppointmentSlotPicker
            :rows-per-page="5"
            v-model="selectedAppointmentSlot"
            :readOnly="!userCanEdit"
          />

          <Button
            label="Opslaan"
            class="mt-4"
            @click="handleSubmit"
            :disabled="!formValid || !userCanEdit"
          />
        </TabPanel>
        <TabPanel value="1" v-if="appointment">
          <FormTableEntity
            :required-forms="appointment.required_forms"
            v-model:show-form-crud="showAppointmentFormCrud"
            :appointment-id="appointment.id"
          />
        </TabPanel>
        <TabPanel value="2" v-if="appointment">
          <FileCrudAppointment :appointment-id="appointment.id" />
        </TabPanel>

        <TabPanel value="3" v-if="appointment">
          <Button
            :variant="'text'"
            :icon="PrimeIcons.LINK"
            label="Bekijk gekoppeld traject"
            v-if="appointment && appointment.track"
            @click="showTrackCrud = true"
          />
          <Dialog
            v-model:visible="showTrackCrud"
            header="Traject"
            :modal="true"
            :dismissable-mask="true"
          >
            <TrackCrud :track-id="appointment?.track?.id" :case-id="caseId" />
          </Dialog>
        </TabPanel>
        <TabPanel value="4" v-if="appointment && me?.permissions.includes('comment:read')">
          <CommentCrud :appointment-id="appointment.id" />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </DialogCrud>
</template>

<style scoped>
h2 {
  font-size: 1em;
}
</style>
