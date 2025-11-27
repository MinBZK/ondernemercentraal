<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'
const { notify } = useNotification()

const props = defineProps<{
  clientId: string
}>()

const allowEdit = ref<boolean>(false)

const clientLocationFormFieldConfig = computed(
  (): FormField<components['schemas']['ClientUpdate']['location']>[] => {
    return [
      {
        key: 'residence_location',
        label: () => clientLabels.residence_location(),
        type: 'text',
        optional: false,
        readOnly: !allowEdit.value,
      },
      {
        key: 'company_location',
        label: () => clientLabels.company_location(),
        type: 'text',
        optional: false,
        readOnly: !allowEdit.value,
      },
    ]
  },
)

const clientDetailFormFieldConfig = computed(
  (): FormField<components['schemas']['ClientUpdate']['details']>[] => {
    return [
      {
        key: 'initials',
        optional: true,
        label: () => clientLabels.initials(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'last_name_prefix',
        optional: true,
        label: () => clientLabels.last_name_prefix(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'last_name',
        optional: false,
        label: () => clientLabels.last_name(),
        type: 'text',
        readOnly: !allowEdit.value,
      },

      {
        key: 'bsn',
        optional: true,
        label: () => clientLabels.bsn(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'phone_number',
        optional: true,
        label: () => clientLabels.phone_number(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'email',
        optional: false,
        type: 'text',
        label: () => clientLabels.email(),
        readOnly: !allowEdit.value,
      },
      {
        key: 'kvk_number',
        optional: true,
        label: () => clientLabels.kvk_number(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'company_name',
        optional: false,
        label: () => clientLabels.company_name(),
        type: 'text',
        readOnly: !allowEdit.value,
      },
      {
        key: 'agree_to_share_data',
        optional: false,
        label: () => clientLabels.agree_to_share_data(),
        type: 'checkbox',
        readOnly: true,
      },
    ]
  },
)

const clientId = toRef(props, 'clientId')
const { clientLabels } = useEntityLabels()
const { client, fetch, updateClient } = useClient(clientId)
fetch()

const clientLocationState = reactive({
  formStateValues: {},
  isValid: true,
})
const clientDetailState = reactive({
  formStateValues: {},
  isValid: true,
})

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const clientUpdate = schemas.ClientUpdate.strict()
  const clientUpdatePayload = {
    details: clientDetailState.formStateValues,
    location: clientLocationState.formStateValues,
  }
  const parsedPayload = clientUpdate.parse(clientUpdatePayload)
  const { data: responseMessage } = await updateClient(parsedPayload)
  if (responseMessage?.message) {
    notify({
      message: responseMessage.message,
    })
  }
  emit('update')
}

const { me } = useAuth()
</script>

<template>
  <div class="flex items-center space-x-2 mb-4" v-if="me?.permissions.includes('client:update')">
    <ToggleSwitch :input-id="'edit'" v-model="allowEdit" />
    <label for="edit">Gegevens bewerken</label>
  </div>
  <FormFieldList
    :form-field-config="clientLocationFormFieldConfig"
    :data="client"
    @update-state="(v) => Object.assign(clientLocationState, v)"
  />
  <FormFieldList
    :form-field-config="clientDetailFormFieldConfig"
    :data="client"
    @update-state="(v) => Object.assign(clientDetailState, v)"
  />
  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    v-if="me?.permissions.includes('client:update')"
  />
</template>
