<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'
const { t } = useI18n()

const pages = computed((): NavigatieItems[] => [
  {
    label: t('header.newAppointment'),
    routeName: 'AppointmentCreate',
    icon: PrimeIcons.CALENDAR_PLUS,
  },
])

const { config } = useConfig()
const logoPath = computed(() =>
  config.value.tenant_name == 'Gemeente Utrecht'
    ? '/img/logo-utrecht.svg'
    : '/img/logo-generiek.png',
)
</script>

<template>
  <NotificationService />
  <ConfirmationService />
  <Grid>
    <template #header>
      <Header
        :title="t('common.appTitle')"
        :pages="pages.filter((p) => p.hide == undefined || !p.hide)"
        :logo-path="logoPath"
      >
        <template #logo>
          <figure>
            <img alt="Rijksoverheid Logo" :src="logoPath" class="mt-2 h-12 md:h-27" />
          </figure>
        </template>
      </Header>
    </template>

    <router-view name="error" />

    <router-view v-slot="{ Component }">
      <transition name="slide-fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <template #footer>
      <Footer />
    </template>
  </Grid>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.005s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.1s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.1s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style>
