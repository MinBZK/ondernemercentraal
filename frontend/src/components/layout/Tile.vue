<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="mr-2 mb-4">
    <h4 class="my-0">
      {{ title }}
    </h4>
    <slot />
  </div>
</template>
