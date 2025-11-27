<script setup lang="ts">
const { createdClient, resendConfirmationEmail } = useClient()

const router = useRouter()
if (!createdClient.value) {
  router.push({ name: 'AppointmentCreate' })
}

const { t } = useLocale()
</script>

<template>
  <Page :page-title="t('pages.appointment.clientCreated.title')">
    <template v-if="createdClient && createdClient.active_case?.initial_appointment">
      <p>
        {{
          t('pages.appointment.clientCreated.clientAlreadyExists', { email: createdClient.email })
        }}
      </p>
      <p>{{ t('pages.appointment.clientCreated.emailSent') }}</p>
    </template>
    <template v-else-if="createdClient">
      <p>{{ t('pages.appointment.clientCreated.ok') }}</p>

      <p>{{ t('pages.appointment.clientCreated.noEmailReceived') }}</p>

      <form @submit.prevent="resendConfirmationEmail(createdClient.id)">
        <Button class="mt-2" type="submit">{{
          t('pages.appointment.clientCreated.resendEmail')
        }}</Button>
      </form>
    </template>
  </Page>
</template>
