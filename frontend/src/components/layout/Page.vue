<script setup lang="ts">
import ProgressSpinner from 'primevue/progressspinner'
import { PrimeIcons } from '@primevue/core/api'
import { useHead } from '@unhead/vue'
const { t } = useI18n()

type CustomRoute = {
  name: string
  params?: Record<string, string | number | null>
}

type ParentRoute = {
  label: string
  route: CustomRoute
}

const props = withDefaults(
  defineProps<{
    pageTitle: string
    loading?: boolean
    showActions?: boolean
    parentRoute?: ParentRoute
    moreInfo?: string | string[]
  }>(),
  {
    loading: false,
    showActions: true,
    useSidebar: false,
  },
)

const pageTitle = toRef(props, 'pageTitle')
const pageTitleInMeta = computed(() => `${pageTitle.value} | ${t('common.appTitle')}`)

useHead({
  title: pageTitleInMeta,
})
</script>

<template>
  <div id="main" :class="['py-4 gap-x-14']">
    <div><slot name="left" /></div>
    <div>
      <p v-if="parentRoute" class="m-0">
        <router-link :to="parentRoute.route">
          <i :class="PrimeIcons.ARROW_CIRCLE_LEFT" class="icon mt-4" />
          {{ parentRoute.label }}
        </router-link>
      </p>
      <h1 v-if="pageTitle" class="mt-4 mb-2">
        {{ pageTitle }}
        <InfoButton v-if="moreInfo" :title="pageTitle" :message="moreInfo" />
      </h1>

      <div class="mb-4">
        <slot name="status" />
      </div>
      <slot v-if="!loading" />

      <div class="text-center">
        <ProgressSpinner v-if="loading" animation-duration=".5s" />
      </div>
    </div>
  </div>
</template>

<style scoped>
i {
  font-size: 0.9em;
}

a {
  text-decoration: none;
  color: var(--primary);
}

h1 {
  margin-top: 0;
}

:deep(p) {
  margin-bottom: 1em;
}
</style>
