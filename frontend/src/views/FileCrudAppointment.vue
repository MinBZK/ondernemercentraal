<script setup lang="ts">
defineProps<{
  appointmentId: string
}>()
</script>

<template>
  <FileCrud :appointment-id="appointmentId" :required-file-types="[]" />
</template>
