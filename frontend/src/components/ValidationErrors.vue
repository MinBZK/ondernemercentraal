<script setup lang="ts">
import type { components } from '@/api/schema'

type Validation = components['schemas']['PayloadValidation']

defineProps<{
  validation: Validation
}>()

const show = defineModel<boolean>({ default: false })
</script>

<template>
  <p>
    <span v-if="validation && !validation.is_valid" class="my-2"
      >Het formulier is nog niet juist ingevuld.
      <span class="underline font-bold cursor-pointer" @click="show = true"
        >Bekijk invulfouten.</span
      ></span
    >
    <Dialog v-model:visible="show" header="Invulfouten" :dismissable-mask="true" class="max-w-3xl">
      <ul>
        <li
          v-for="(error, index) in validation.validation_errors"
          :key="index"
          class="py-2 border-b-1 border-solid border-gray-300"
        >
          {{ error.readable_message }}
        </li>
      </ul>
      <template #footer><Button label="Sluiten" @click="show = false" /></template>
    </Dialog>
  </p>
</template>
