<script setup lang="ts">
import type { FileTableProps } from './FileCrud.vue'

defineProps<
  {
    caseId: string
  } & FileTableProps
>()
</script>

<template>
  <FileCrud :case-id="caseId" :required-file-types="requiredFileTypes" />
</template>
