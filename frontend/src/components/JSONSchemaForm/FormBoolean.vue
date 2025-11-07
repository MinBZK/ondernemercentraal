<script setup lang="ts">
defineProps<{
  hasMissingRequiredValue: boolean
  readonly: boolean
}>()

const selectedValue = defineModel<boolean>({ default: false })
</script>

<template>
  <ToggleSwitch v-model="selectedValue" />
</template>
