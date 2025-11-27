<script setup lang="ts">
import { joinStringsSemantic } from '@/util'

const { config } = useConfig()
</script>

<template>
  <Page
    page-title="Partnerorganisaties"
    :more-info="`Gebruik de dienstverleningen ${joinStringsSemantic(config.required_products, 'of', true)} om partnerorganisaties te koppelen aan toekomstgesprekken of SHVO-gesprekken.`"
  >
    <PartnerOrganizationTable />
  </Page>
</template>
