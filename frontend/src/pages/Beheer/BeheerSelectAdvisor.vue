<script setup lang="ts">
import type { components } from '@/api/schema'

type Advisor = components['schemas']['UserBase']

const props = defineProps<{
  caseId: string
  selectedAdvisor?: Advisor
}>()

const selectedAdvisor = toRef(props, 'selectedAdvisor')

const { updateAdvisor } = useCase()
const { me } = useAuth()
</script>

<template>
  <div>
    <BeheerSelectUser
      :initialUserId="selectedAdvisor?.id"
      :caseId="props.caseId"
      :modelValue="selectedAdvisor"
      :disabled="!me?.permissions.includes('case:update')"
      @update:modelValue="
        (newAdvisor) => {
          if (newAdvisor?.id !== selectedAdvisor?.id) {
            updateAdvisor(caseId, newAdvisor?.id)
          }
        }
      "
      :roleNames="['adviseur', 'beheerder']"
    />
  </div>
</template>
