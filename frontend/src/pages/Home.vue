<script setup lang="ts">
const { t } = useI18n()
</script>

<template>
  <Page :page-title="t('common.welcome')">
    {{ t('common.appTitle') }}
  </Page>
</template>
