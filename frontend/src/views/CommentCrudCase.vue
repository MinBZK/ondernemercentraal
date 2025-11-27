<script setup lang="ts">
import type { CommentCrudProps } from './CommentCrud.vue'

defineProps<
  {
    caseId: string
  } & CommentCrudProps
>()
</script>

<template>
  <CommentCrud :case-id="caseId" />
</template>
