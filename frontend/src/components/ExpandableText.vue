<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'

defineProps<{
  header: string
  descriptionShort?: string
  description?: string
}>()

const expanded = ref<boolean>(false)
</script>

<template>
  <div class="px-2 py-4 rounded-lg block cursor-pointer" @click="expanded = !expanded">
    <p class="mb-0">
      <strong
        ><i :class="[expanded ? PrimeIcons.MINUS : PrimeIcons.PLUS, 'mr-2 text-primary/50']" />
        {{ header }}</strong
      >
      - {{ descriptionShort }}
    </p>

    <div :class="['content', expanded ? 'active' : 'hidden']" v-if="description">
      <div class="bg-gray-100 rounded-xl p-4 mt-2">
        <MarkdownText :text="description" />
      </div>
    </div>

    <div class="text-primary mt-4">
      <icon :class="expanded ? PrimeIcons.CHEVRON_UP : PrimeIcons.CHEVRON_DOWN" />
      {{ !expanded ? 'Toon meer informatie' : 'Verberg extra informatie' }}
    </div>
  </div>
</template>

<style scoped>
p {
  margin-bottom: 0 !important;
}
</style>
