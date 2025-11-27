<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

type Appointment = components['schemas']['Appointment']

const props = withDefaults(
  defineProps<{
    caseId?: string
    showCreate?: boolean
    showCaseLink?: boolean
  }>(),
  {
    showCreate: true,
    showCaseLink: false,
  },
)

const caseId = toRef(props, 'caseId')
const { appointments, fetchMany } = useAppointments(caseId)
fetchMany()

const { appointmentLabels } = useEntityLabels()

const appointmentTableConfigPartner: TableColumnConfig<Appointment>[] = [
  {
    key: 'appointment_type_name',
    label: appointmentLabels.appointment_type_name,
  },
  {
    key: 'case_number',
    label: appointmentLabels.case_number,
    dataType: 'custom',
  },
  {
    key: 'client_initials',
    label: appointmentLabels.client_initials,
  },
  {
    key: 'client_last_name',
    label: appointmentLabels.client_last_name,
  },
  {
    key: 'client_residence_location',
    label: appointmentLabels.client_residence_location,
  },
  {
    key: 'client_phone_number',
    label: appointmentLabels.client_phone_number,
  },
  {
    key: 'client_email',
    label: appointmentLabels.client_email,
  },
]

const appointmentTableConfigDefault: TableColumnConfig<components['schemas']['Appointment']>[] = [
  {
    key: 'appointment_type_name',
    label: appointmentLabels.appointment_type_name,
  },
  {
    key: 'partner_organization_name',
    label: appointmentLabels.partner_organization_name,
  },
]

const appointmentTableConfig: TableColumnConfig<components['schemas']['Appointment']>[] = [
  ...(props.caseId ? appointmentTableConfigDefault : appointmentTableConfigPartner),
  {
    key: 'start_time',
    label: () => 'Datum',
    dataType: 'date',
  },
  {
    key: 'start_time',
    label: () => 'Van',
    dataType: 'time',
  },
  {
    key: 'end_time',
    label: () => 'Tot',
    dataType: 'time',
  },
  {
    key: 'status',
    label: () => 'Status',
  },
]

const showAppointmentCrud = ref(false)

const { deleteAppointment } = useAppointment()

const { me } = useAuth()
const { askToConfirm } = useConfirm()

type Permissions = components['schemas']['UserWithPermissions']['permissions']

const requiredCrudPermissions: Permissions = ['appointment:read']

const route = useRoute()
const routeName = computed(() => route.name)

watch(routeName, (newRouteName, oldRouteName) => {
  if (newRouteName !== oldRouteName) {
    fetchMany()
  }
})

const canEdit = computed(() =>
  requiredCrudPermissions.some((p) => me.value?.permissions.includes(p)),
)
</script>

<template>
  <router-link
    :to="{ name: 'BeheerCaseAppointmentCreate', params: { caseId } }"
    v-if="me?.permissions.includes('track:create') && showCreate"
  >
    <Button
      @click="showAppointmentCrud = true"
      size="small"
      :variant="'outlined'"
      :icon="PrimeIcons.PLUS"
      label="Gesprek"
    />
  </router-link>

  <OcTable
    :data="appointments"
    :table-config="appointmentTableConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
    :row-link-config="
      canEdit
        ? {
            routeName: 'BeheerCaseAppointmentDetail',
            params: [
              {
                routeIdKey: 'appointmentId',
                idKey: 'id',
              },
              {
                routeIdKey: 'caseId',
                idKey: 'case_id',
              },
            ],
          }
        : undefined
    "
  >
    <template #action="{ row: currentAppointment }">
      <ContextMenu
        :menu-items="[
          {
            icon: PrimeIcons.TRASH,
            label: 'Verwijderen',
            hide: !me?.permissions.includes('appointment:delete'),
          },
        ]"
        @item-clicked="
          async (item) => {
            if (item.label == 'Verwijderen') {
              await askToConfirm({
                question: `Weet je zeker dat je het gesprek '${currentAppointment.appointment_type_name}' wilt verwijderen?`,
                title: 'Gesprek verwijderen',
              })
              await deleteAppointment(currentAppointment.id)
              fetchMany()
            }
          }
        "
      />
    </template>
    <template #custom="{ column, row: currentAppointment }">
      <template v-if="column.key == 'case_number'">
        <router-link
          v-if="column.key == 'case_number'"
          :to="{
            name: 'BeheerCaseDetail',
            params: { caseId: currentAppointment.case_id },
          }"
          >{{ currentAppointment.case_number }}</router-link
        >
      </template>
    </template>
  </OcTable>
</template>
