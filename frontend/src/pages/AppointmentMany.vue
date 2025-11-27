<script setup lang="ts">
const { t } = useLocale()
</script>

<template>
  <Page :page-title="t('common.appTitle')">
    {{ t('common.welcome') }}
  </Page>
</template>
