<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

type Track = components['schemas']['TrackBase']

type TrackView = components['schemas']['Track']

const props = withDefaults(
  defineProps<{
    caseId?: string
    showCaseLink?: boolean
  }>(),
  { showCaseLink: false },
)

const caseId = toRef(props, 'caseId')
const trackId = ref()
const { tracks, fetchMany } = useTrack(trackId, caseId)

fetchMany()

const showTrackCrud = ref(false)
const { me } = useAuth()
const { trackLabels } = useEntityLabels()

const selectedTrack = ref<Track>()

const trackTableConfigDefault: TableColumnConfig<TrackView>[] = [
  {
    key: 'partner_organization_name',
    label: trackLabels.partner_organization_name,
  },
]
const trackTableConfigPartner: TableColumnConfig<TrackView>[] = [
  {
    key: 'case_number',
    label: trackLabels.case_number,
    dataType: 'custom',
  },
  {
    key: 'client_initials',
    label: trackLabels.client_initials,
  },
  {
    key: 'client_last_name',
    label: trackLabels.client_last_name,
  },
  {
    key: 'client_residence_location',
    label: trackLabels.client_residence_location,
  },
  {
    key: 'client_phone_number',
    label: trackLabels.client_phone_number,
  },
  {
    key: 'client_email',
    label: trackLabels.client_email,
  },
]

const trackTableBase = computed(() =>
  me.value?.role_name == 'partner' ? trackTableConfigPartner : trackTableConfigDefault,
)

const trackTableConfig: TableColumnConfig<TrackView>[] = [
  {
    key: 'track_type_name',
    label: trackLabels.track_type_name,
  },
  ...trackTableBase.value,
  {
    key: 'status',
    label: trackLabels.status,
    dataType: 'text',
  },

  {
    key: 'start_dt',
    label: trackLabels.start_dt,
    dataType: 'datetime',
  },
  {
    key: 'end_dt',
    label: trackLabels.end_dt,
    dataType: 'datetime',
  },
]

watch(showTrackCrud, (newValue) => {
  if (!newValue) {
    selectedTrack.value = undefined
  }
})

const route = useRoute()
const routeName = computed(() => route.name)
watch(routeName, (newRouteName, oldRouteName) => {
  if (newRouteName !== oldRouteName) {
    fetchMany()
  }
})
</script>

<template>
  <router-link
    v-if="me?.permissions.includes('track:create')"
    :to="{
      name: 'BeheerCaseTrackCreate',
      params: { caseId },
    }"
  >
    <Button
      @click="showTrackCrud = true"
      size="small"
      :variant="'outlined'"
      :icon="PrimeIcons.PLUS"
      label="Traject"
    />
  </router-link>

  <OcTable
    :data="tracks"
    :table-config="trackTableConfig"
    :id-key="'id'"
    :limit="5"
    :row-link-config="
      me?.permissions.includes('track:read')
        ? {
            routeName: 'BeheerCaseTrackDetail',
            params: [
              {
                routeIdKey: 'trackId',
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
    show-action-column
  >
    <template #custom="{ column, row: currentTrack }">
      <template v-if="column.key == 'case_number'">
        <router-link
          v-if="column.key == 'case_number'"
          :to="{
            name: 'BeheerCaseDetail',
            params: { caseId: currentTrack.case.id },
          }"
          >{{ currentTrack.case_number }}</router-link
        >
      </template>
    </template>
  </OcTable>
</template>
