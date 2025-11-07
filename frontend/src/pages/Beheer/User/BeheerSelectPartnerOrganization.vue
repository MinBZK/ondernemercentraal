<script setup lang="ts">
const { trackValues, fetch } = useTrackValue()

fetch()

const selectedPartnerOrganization = defineModel<string>({
  required: false,
})
</script>

<template>
  <Select
    v-model="selectedPartnerOrganization"
    class="w-full"
    input-id="select-track-partner"
    :options="trackValues?.partner_organization"
    optionLabel="name"
    :show-clear="true"
    placeholder="Kies partnerorganisatie"
  />
</template>
