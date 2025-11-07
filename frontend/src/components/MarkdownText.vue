<script setup lang="ts">
import { marked } from 'marked'

const props = defineProps<{
  text: string
}>()

const parsedText = computed(() => {
  return marked.parse(props.text)
})
</script>

<template>
  <div v-html="parsedText" class="markdown"></div>
</template>
