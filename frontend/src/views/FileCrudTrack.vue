<script setup lang="ts">
import type { FileTableProps } from './FileCrud.vue'

defineProps<
  {
    trackId: string
  } & FileTableProps
>()
</script>

<template>
  <FileCrud :track-id="trackId" :required-file-types="requiredFileTypes" />
</template>
