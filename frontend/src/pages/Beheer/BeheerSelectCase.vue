<script setup lang="ts">
import type { components } from '@/api/schema'

type Case = components['schemas']['CaseBase']

const props = withDefaults(
  defineProps<{
    initialCaseId?: string
    readOnly?: boolean
  }>(),
  {
    readOnly: false,
  },
)

const { me } = useAuth()
const initialCaseId = toRef(props, 'initialCaseId')
const { cases, fetchCases } = useCase()
fetchCases()
const selectedCase = defineModel<Case>({ required: false })
const editAllowed = computed(
  () => me.value?.permissions.includes('task:update:case') && !props.readOnly,
)
watch(
  [cases, initialCaseId],
  () => {
    selectedCase.value = cases.value.find((c) => c.id === initialCaseId.value)
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <IftaLabel>
    <Select
      v-model="selectedCase"
      class="w-full"
      input-id="select-case"
      :options="cases"
      optionLabel="description"
      :show-clear="true"
      placeholder="Selecteer dossier"
      :disabled="!editAllowed"
      filter
    />
    <label :for="'select-case'">Dossier</label>
  </IftaLabel>
</template>
