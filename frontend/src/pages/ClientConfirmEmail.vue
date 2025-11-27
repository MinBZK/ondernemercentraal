<script setup lang="ts">
import { useRouteQuery } from '@vueuse/router'
import { PrimeIcons } from '@primevue/core/api'

const { confirmEmail } = useClient()

const emailConfirmed = ref<boolean>()

const token = useRouteQuery('confirmation_token')
const tokenParsed = computed(
  () => (Array.isArray(token.value) ? token.value[0] : token.value) || '',
)

async function handleConfirm() {
  const data = await confirmEmail(tokenParsed.value)
  if (data.error) {
    emailConfirmed.value = false
  } else {
    emailConfirmed.value = true
  }
}

handleConfirm()
</script>

<template>
  <Page :page-title="'Emailadres bevestigen'">
    <Message v-if="emailConfirmed" :severity="'success'" :icon="PrimeIcons.CHECK"
      >Jouw emailadres is succesvol bevestigd.</Message
    >
    <Message
      v-else-if="emailConfirmed === false"
      :severity="'error'"
      :icon="PrimeIcons.EXCLAMATION_TRIANGLE"
      >Er is een fout opgetreden bij het bevestigen van jouw emailadres.</Message
    >
  </Page>
</template>
