<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'

defineProps<{
  message: string[] | string
  title: string
}>()

const showDialog = ref<boolean>(false)
</script>

<template>
  <Button
    :icon="PrimeIcons.INFO_CIRCLE"
    size="small"
    rounded
    :variant="'text'"
    @click="showDialog = !showDialog"
  />
  <Dialog
    v-model:visible="showDialog"
    :header="title"
    :modal="true"
    :dismissable-mask="true"
    @update:visible="showDialog = false"
    :style="{ width: '50rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    >{{ message }}</Dialog
  >
</template>
