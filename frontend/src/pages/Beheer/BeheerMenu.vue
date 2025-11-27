<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'

const { me } = useAuth()
const { config } = useConfig()
const { keycloak } = useKeycloak()

type BeheerItemBase = {
  show: boolean
}

type BeheerItemLink = BeheerItemBase & {
  label: string
  routeName: string
  routeParams?: Record<string, string>
  icon?: string
  type: 'link'
}

type BeheerItemSeperator = BeheerItemBase & {
  type: 'seperator'
}

type BeheerItem = BeheerItemLink | BeheerItemSeperator

const menuItems = computed((): BeheerItem[] => {
  return [
    {
      label: 'Dossiers',
      routeName: 'BeheerCaseMany',
      icon: PrimeIcons.FOLDER,
      show: Boolean(me.value?.permissions.includes('case:update')),
      type: 'link',
    },
    {
      label: 'Beschikbaarheid',
      routeName: 'BeheerAvailability',
      icon: PrimeIcons.CALENDAR,
      show: Boolean(me.value?.permissions.includes('availability:read')),
      type: 'link',
    },

    {
      label: 'Trajecten',
      routeName: 'BeheerTrackMany',
      icon: PrimeIcons.BRIEFCASE,
      show: me.value?.role_name == 'partner',
      type: 'link',
    },
    {
      label: 'Gesprekken',
      routeName: 'BeheerAppointmentMany',
      icon: PrimeIcons.USERS,
      show: me.value?.role_name == 'partner',
      type: 'link',
    },
    {
      label: `Mijn dossier`,
      routeName: 'BeheerCaseDetail',
      routeParams: { caseId: me.value?.active_case_id || '' },
      icon: PrimeIcons.BRIEFCASE,
      show: me.value?.role_name == 'ondernemer' && Boolean(me.value.active_case_id),
      type: 'link',
    },
    {
      label: `Taken`,
      routeName: 'BeheerTaskMany',
      icon: PrimeIcons.LIST,
      show: Boolean(me.value?.permissions.includes('task:read')),
      type: 'link',
    },
    {
      label: 'Formulieren',
      routeName: 'BeheerFormMany',
      icon: PrimeIcons.FILE_EDIT,
      show: Boolean(me.value?.permissions.includes('case:update')),
      type: 'link',
    },
    {
      type: 'seperator',
      show: Boolean(me.value?.permissions.includes('user:create')),
    },
    {
      label: 'Gebruikers',
      routeName: 'BeheerUserMany',
      icon: PrimeIcons.USERS,
      show: Boolean(me.value?.permissions.includes('user:create')),
      type: 'link',
    },
    {
      label: 'Pijlers',
      routeName: 'BeheerProductMany',
      icon: PrimeIcons.BRIEFCASE,
      show: Boolean(me.value?.permissions.includes('product:create')),
      type: 'link',
    },
    {
      label: 'Partnerorganisaties',
      routeName: 'BeheerPartnerOrganizationMany',
      icon: PrimeIcons.BUILDING,
      show: Boolean(me.value?.permissions.includes('partner-organization:create')),
      type: 'link',
    },
  ]
})

const route = useRoute()
</script>

<template>
  <div class="mt-2">
    <template v-for="(item, index) in menuItems" :key="index">
      <Divider v-if="item.type == 'seperator' && item.show" />
      <router-link
        v-if="item.type !== 'seperator' && item.show"
        :to="{ name: item.routeName, params: item.routeParams }"
        :class="[
          'inline-block p-2 w-full hover:bg-primary/13 rounded-md text-primary',
          {
            'bg-primary/7 hover:bg-primary/13': route.name === item.routeName,
          },
        ]"
      >
        <i :class="item.icon" class="inline-icon mr-1" />
        {{ item.label }}
      </router-link>
    </template>

    <Divider />

    <a
      @click.prevent="keycloak?.logout()"
      :class="[
        'inline-block p-2 w-full hover:bg-primary/13 rounded-md text-primary cursor-pointer',
      ]"
    >
      <i :class="PrimeIcons.SIGN_OUT" class="inline-icon mr-1" />
      Uitloggen
    </a>
    <button
      v-ripple
      class="relative overflow-hidden w-full border-0 hover:bg-primary/10 px-2 pt-2 pb-1 rounded-lg flex items-start transition-colors duration-200"
    >
      <Avatar class="mr-2" shape="circle" :label="me?.name.slice(0, 1)" />
      <span class="inline-flex flex-col items-start">
        <span class="font-bold">{{ me?.name }}</span>
        <span class="text-sm">{{ me?.role_name }}</span>
      </span>
    </button>
    <Divider />
    <span class="text-gray-400">Versie {{ config.app_version }}</span>
  </div>
</template>

<style scoped>
h2 {
  margin-bottom: 0;
  font-size: 1.25em;
}

a {
  text-decoration: none;
}
</style>
