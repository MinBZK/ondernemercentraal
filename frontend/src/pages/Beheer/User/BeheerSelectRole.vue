<script setup lang="ts">
import type { components } from '@/api/schema'

type Role = components['schemas']['Role']

const { roles, fetchMany } = useRole()
fetchMany()

const selectedRole = defineModel<Role>({
  required: false,
})
</script>

<template>
  <Select
    v-model="selectedRole"
    class="w-full"
    input-id="select-user"
    :options="roles"
    optionLabel="name"
    :show-clear="true"
    placeholder="Selecteer gebruiker"
  />
</template>
