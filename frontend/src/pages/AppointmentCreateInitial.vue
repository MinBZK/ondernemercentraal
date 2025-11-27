<script setup lang="ts">
import type { components } from '@/api/schema'
import { useRouteQuery } from '@vueuse/router'
import { formatTimeSlot } from '@/util/format'
const { t } = useLocale()

const {
  fetchFromToken: fetchClientFromToken,
  createdClient,
  loading,
  resendConfirmationEmail,
} = useClient()

const { createAppointmentPublic } = useAppointment(undefined)

const token = useRouteQuery('confirmation_token')
const tokenParsed = computed(
  () => (Array.isArray(token.value) ? token.value[0] : token.value) || '',
)

watch(
  token,
  () => {
    fetchClientFromToken(tokenParsed.value)
  },
  {
    immediate: true,
  },
)

type AppointmentSlot = components['schemas']['AppintmentSlotWithAvailability']

async function handleCreateAppointment() {
  if (!createdClient.value) {
    throw new Error('Client is not defined')
  }
  if (!selectedAppointmentSlot.value) {
    throw new Error('Selected appointment is not defined')
  }
  await createAppointmentPublic(
    tokenParsed.value,
    selectedAppointmentSlot.value?.start_time,
    selectedAppointmentSlot.value?.end_time,
  )
  fetchClientFromToken(tokenParsed.value)
}

const email = ref<string>('')

const { isMobile } = useResponsive()

const selectedAppointmentSlot = ref<AppointmentSlot>()

const initialAppointment = computed(() => {
  return createdClient.value?.active_case?.initial_appointment
})

const formattedTimeSlot = computed(() => {
  const start = initialAppointment.value?.start_time
  const end = initialAppointment.value?.end_time
  if (!start) throw new Error('Start time is not defined')
  if (!end) throw new Error('End time is not defined')
  return formatTimeSlot(start, end)
})
</script>

<template>
  <Page
    :page-title="
      createdClient?.active_case?.initial_appointment
        ? t('pages.appointment.pick.titleCreated')
        : t('pages.appointment.pick.title')
    "
  >
    <template v-if="!loading && !createdClient">
      <p>{{ t('pages.appointment.pick.invalidLink') }}</p>

      <form @submit.prevent="resendConfirmationEmail(undefined, email)">
        <IftaLabel class="mt-2">
          <InputText
            v-model="email"
            :class="[isMobile ? 'w-full' : 'w-[300px]']"
            :input-id="'email'"
            :name="'email'"
            type="text"
            :placeholder="'E-mail adres'"
          />
          <label :for="'email'">E-mail</label>
        </IftaLabel>

        <Button class="my-2" label="Verstuur een nieuwe link" type="submit" />
      </form>
      <p class="mt-2">
        <router-link :to="{ name: 'AppointmentCreate' }">
          {{ t('pages.appointment.pick.signUpAgain') }}
        </router-link>
      </p>
    </template>
    <template v-else-if="initialAppointment">
      {{ t('pages.appointment.pick.created') }}
      <strong>{{ formattedTimeSlot }} </strong>.
    </template>
    <template v-else-if="createdClient && !initialAppointment">
      <AppointmentSlotPicker
        v-model="selectedAppointmentSlot"
        :only-show-slots-with-advisors-available="true"
      />

      <form @submit.prevent="handleCreateAppointment">
        <Button
          class="my-2"
          :label="t('pages.appointment.pick.pickButtonLabel')"
          type="submit"
          :disabled="!selectedAppointmentSlot"
        />
      </form>
    </template>
  </Page>
</template>
