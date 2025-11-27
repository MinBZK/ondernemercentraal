<script setup lang="ts">
import { joinStringsSemantic } from '@/util'

const { config } = useConfig()
</script>

<template>
  <Page page-title="Pijlers en diensten">
    <h2>Pijlers</h2>
    <ProductCategoryTable />
    <h2 class="mt-4">
      Dienstverleningen

      <InfoButton
        title="Informatie over dienstverleningen"
        :message="`De dienstverleningen ${joinStringsSemantic(config.required_products, 'en', true)} kunnen
      niet worden verwijderd omdat deze nodig zijn voor toekomstgesprekken en
      SHVO-gesprekken.`"
      />
    </h2>

    <ProductTable />
  </Page>
</template>
