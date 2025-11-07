<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'
const { notify } = useNotification()

const props = defineProps<{
  user?: components['schemas']['User']
}>()

const { create, update } = useUser()
const { roles, fetchMany: fetchRoles } = useRole()
const { trackValues, fetch: fetchTrackValues } = useTrackValue()
const { userLabels } = useEntityLabels()
fetchRoles()
fetchTrackValues()

const emit = defineEmits<{
  submit: []
}>()

async function handleSubmit() {
  const payload = schemas.UserCreate.strict().parse(userStateNew)

  try {
    if (!props.user) {
      const { data } = await create(payload)
      if (!data) throw new Error('Failed to create user')
      const { message } = data
      notify({ message })
    } else {
      await update(props.user.id, payload)
    }
    emit('submit')
  } catch (e) {
    console.error(e)
  }
}

const userConfig = computed((): FormField<components['schemas']['UserCreate']>[] => {
  return [
    {
      key: 'name',
      label: () => userLabels.name(),
      type: 'text',
      optional: false,
    },
    {
      key: 'role_name',
      label: () => userLabels.role(),
      type: 'select',
      optional: false,
      options: roles.value.map((r) => r.name),
    },
    {
      key: 'partner_organization_name',
      label: () => userLabels.partner_organization_name(),
      type: 'select',
      options: trackValues?.value?.partner_organization.map((p) => p.name),
      optional: true,
    },
    {
      key: 'active',
      label: () => userLabels.active(),
      type: 'checkbox',
      optional: false,
      defaultValue: true,
    },
  ]
})

const userStateNew: Record<keyof components['schemas']['UserCreate'], unknown> = reactive({
  active: undefined,
  name: undefined,
  role_name: undefined,
  partner_organization_name: undefined,
})
const formIsValid = ref(false)
</script>

<template>
  <FormFieldList
    :form-field-config="userConfig"
    :data="user"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(userStateNew, formStateValues)
        formIsValid = isValid
      }
    "
    :n-columns="1"
  />

  <Button
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    class="mt-4"
    @click="handleSubmit"
    :disabled="!formIsValid"
  />
</template>
