<script setup lang="ts">
import { sortArrayByKey } from '@/util'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  trackId: string
}>()

const caseId = ref()
const trackId = toRef(props, 'trackId')
const { track, fetch: fetchTrack, updateTrackPartnerOrganization } = useTrack(trackId, caseId)
const { partnerOrganizations, fetch: fetchPartnerOrganizations } = usePartnerOrganization()
fetchTrack()
fetchPartnerOrganizations()

const trackLabel = computed(() => track.value?.track_type_name.toLocaleLowerCase())
const productCategoryName = computed(() => track.value?.product_category_name)

const allowedPartnerOrgs = computed(() => {
  return partnerOrganizations.value.filter((p) => {
    if (!productCategoryName.value) {
      throw new Error('Product category name is not defined')
    }
    return p.product_category_names.includes(productCategoryName.value)
  })
})

async function selectPartnerOrganization(name: string) {
  if (!track.value) {
    throw new Error('Track is not defined')
  }
  await updateTrackPartnerOrganization(track.value.id, name)
  fetchTrack()
}
</script>

<template>
  <Page :page-title="`Partnerorganisatie kiezen voor ${trackLabel}`">
    <p class="mb-4">
      Je komt in aanmerking voor hulp bij de pijler '{{ track?.product_category_name }}'. Kies een
      partnerorganisatie die je hierbij kunt gaan helpen.
    </p>
    <Divider />
    <template v-if="track?.partner_organization_name">
      <Message :severity="'success'" :icon="PrimeIcons.CHECK">
        Je hebt de partnerorganisatie <strong>{{ track.partner_organization_name }}</strong> gekozen
        voor het traject '{{ track.track_type_name }}'.
      </Message>
    </template>
    <template v-else-if="track">
      <ul>
        <template v-for="p in sortArrayByKey(allowedPartnerOrgs, 'name')" :key="p.id">
          <li>
            <ExpandableText
              :header="p.name"
              :description="p.description || undefined"
              :description-short="p.description_short || undefined"
            />
            <Button
              label="Kies deze partnerorganisatie"
              size="small"
              @click.prevent="selectPartnerOrganization(p.name)"
            />
            <Divider />
          </li>
        </template>
      </ul>
    </template>
  </Page>
</template>

<style scoped>
p {
  margin-bottom: 0 !important;
}
</style>
