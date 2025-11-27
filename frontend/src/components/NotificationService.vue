<script setup lang="ts">
import type { Notification } from '@/composables/useNotification'
import { PrimeIcons } from '@primevue/core/api'

const { t } = useLocale()
const { notifications } = useNotification()

watch(
  notifications,
  () => {
    while (notifications.value.length > 0) {
      const n = notifications.value.pop()
      if (n) {
        // toast.add(getToast(n))
        visibleNotification.value = n
        showDrawer.value = true
      }
    }
  },
  { deep: true },
)
const { isMobile } = useResponsive()

const visibleNotification = ref<Notification>()
const showDrawer = ref(false)

function getIcon(severity: Notification['severity']) {
  switch (severity) {
    case 'error':
      return PrimeIcons.EXCLAMATION_TRIANGLE
    case 'info':
      return PrimeIcons.INFO_CIRCLE
    case 'success':
      return PrimeIcons.CHECK_CIRCLE
    case 'warn':
      return PrimeIcons.EXCLAMATION_TRIANGLE
  }
  return PrimeIcons.INFO_CIRCLE
}

const parsedMessages = computed(() => {
  return Array.isArray(visibleNotification.value?.message)
    ? visibleNotification.value?.message
    : [visibleNotification.value?.message]
})
</script>

<template>
  <Toast :position="isMobile ? 'center' : 'top-center'" class="mt-2 text-xl" />
  <Drawer
    v-if="visibleNotification"
    v-model:visible="showDrawer"
    position="bottom"
    class="h-full text-red-400"
    style="height: auto"
    :show-close-icon="false"
  >
    <div
      :class="[
        'py-8 px-4 text-lg max-w-3xl mx-auto',
        {
          'text-red-700': visibleNotification['severity'] === 'error',
          'mb-[100px]': isMobile,
        },
      ]"
    >
      <p v-for="(m, index) in parsedMessages" :key="m" class="mb-4">
        <i
          :class="getIcon(visibleNotification['severity'])"
          class="inline-icon mr-3"
          v-if="index == 0"
        />
        {{ m }}
      </p>

      <Button class="w-full mt-8" @click="showDrawer = false" variant="outlined">{{
        t('common.close')
      }}</Button>
    </div>
  </Drawer>
</template>
