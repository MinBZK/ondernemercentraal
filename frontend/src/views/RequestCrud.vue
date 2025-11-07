<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  requestId?: string
  caseId: string
}>()

const requestId = toRef(props, 'requestId')
const caseId = toRef(props, 'caseId')
const { requestLabels } = useEntityLabels()
const { createRequest, updateRequest, fetch: fetchRequests, requests } = useRequest(caseId)

fetchRequests()

type RequestName = components['schemas']['RequestUpsert']['name']
const request = computed(() => requests.value.find((r) => r.id === requestId.value))
const requestNames: RequestName[] = ['BBZ-aanvraag', 'BBZ-verlenging-aanvraag', 'IOAZ-aanvraag']

const requestConfig = computed((): FormField<components['schemas']['Request']>[] => {
  return [
    {
      key: 'name',
      label: () => requestLabels.name(),
      type: 'select',
      options: requestNames,
      optional: false,
      readOnly: !me.value?.permissions.includes('request:update'),
    },
  ]
})

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const requestCreate = schemas.RequestUpsert.strict()

  // pre-process the state: Zod expects a string while it actually is and should be a Date
  const preprocessedState = { ...state }

  const parsedPayload = requestCreate.parse(preprocessedState)
  if (!requestId.value) {
    await createRequest(parsedPayload)
  } else {
    await updateRequest(parsedPayload, requestId.value)
  }
  emit('update')
}

const { me } = useAuth()
const formIsValid = ref(false)

type RequestStateFormState = Record<keyof components['schemas']['RequestUpsert'], unknown>

const state: RequestStateFormState = reactive({
  name: '',
})
</script>

<template>
  <FormFieldList
    :form-field-config="requestConfig"
    :data="request"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(state, formStateValues)
        formIsValid = isValid
      }
    "
    :n-columns="1"
  />

  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    :disabled="!formIsValid"
    v-if="me?.permissions.includes('request:create') || me?.permissions.includes('request:update')"
  />
</template>
