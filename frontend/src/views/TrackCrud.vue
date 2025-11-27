<script setup lang="ts">
const props = defineProps<{
  caseId?: string
  trackId?: string
}>()
const trackId = toRef(props, 'trackId')
const caseId = toRef(props, 'caseId')
const { track, fetch: fetchTrack } = useTrack(trackId, caseId)
const { products, fetch: fetchProducts } = useProduct()
const { fetch } = useTrackValue()
fetch()
if (props.trackId) fetchTrack()
if (products.value.length === 0) fetchProducts()

const showFormCrud = ref(false)

const { me } = useAuth()

const { navigateToParentRoute } = useParentRoute()
</script>

<template>
  <DialogCrud header="Traject">
    <Tabs value="0">
      <TabList>
        <Tab value="0">Traject</Tab>
        <Tab value="1" v-if="track && track.required_forms.length > 0">Formulieren</Tab>
        <Tab value="2" v-if="track">Bestanden</Tab>
        <Tab value="3" v-if="track && track.appointments.length > 0">Gesprekken</Tab>
        <Tab value="4" v-if="track && me?.permissions.includes('comment:read')">Notities</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <TrackCrudForm
            :track-id="trackId"
            @update-track="navigateToParentRoute()"
            :case-id="caseId"
          />
        </TabPanel>
        <TabPanel value="1" v-if="track">
          <FormTableEntity
            :required-forms="track.required_forms"
            v-model:show-form-crud="showFormCrud"
            :track-id="track.id"
          />
        </TabPanel>
        <TabPanel value="2">
          <template v-if="track">
            <h2 class="mt-4">Bestanden</h2>
            <FileCrudTrack :track-id="track.id" :required-file-types="track.required_file_types" />
          </template>
        </TabPanel>
        <TabPanel value="3" v-if="track && track.appointments.length > 0">
          <AppointmentTable :case-id="track.case_id" :show-create="false" />
        </TabPanel>
        <TabPanel value="4" v-if="track && me?.permissions.includes('comment:read')">
          <CommentCrud :track-id="track.id" />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </DialogCrud>
</template>
