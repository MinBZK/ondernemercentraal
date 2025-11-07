<script setup lang="ts">
const props = defineProps<{
  formId: string
}>()

const formId = toRef(props, 'formId')
const showForm = ref(true)
</script>
<template>
  <DialogForm :form-data-id="formId" v-model="showForm" />
</template>
