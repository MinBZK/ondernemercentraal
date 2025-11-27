<script setup lang="ts">
const { t } = useLocale()
</script>

<template>
  <Page :page-title="t('pages.appointment.confirmed.title')">
    {{ t('pages.appointment.confirmed.confirmationMessage') }}
  </Page>
</template>
