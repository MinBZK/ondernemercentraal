<script setup lang="ts">
import type { components } from '@/api/schema'
import { sortArrayByKey } from '@/util'

type User = components['schemas']['UserBase']

const props = withDefaults(
  defineProps<{
    roleNames?: components['schemas']['Role']['name'][]
    initialUserId?: string
    caseId?: string
    disabled?: boolean
  }>(),
  {
    disabled: false,
  },
)

const selectedUser = defineModel<User>({
  required: false,
})

const caseId = computed(() => props.caseId)
const { users, fetch: fetchUsers } = useUserBasic(caseId)
const initialUserId = computed(() => props.initialUserId)

const { me } = useAuth()

const editAllowed = computed(() => me.value?.permissions.includes('user-basic:read'))
watch(
  editAllowed,
  () => {
    if (editAllowed.value) {
      fetchUsers()
    }
  },
  {
    immediate: true,
  },
)

const filteredUsers = computed(() => {
  if (!props.roleNames) {
    return users.value
  } else if (users.value) {
    return users.value.filter((user) => props.roleNames?.includes(user.role_name))
  }
})

watch(
  [initialUserId, filteredUsers],
  () => {
    const users = filteredUsers.value || []
    if (users.length > 0) {
      selectedUser.value = users.find((u) => u.id === initialUserId.value)
    }
  },
  {
    immediate: true,
  },
)

watch(caseId, () => fetchUsers())
</script>

<template>
  <IftaLabel>
    <Select
      v-model="selectedUser"
      class="w-full"
      input-id="select-user"
      :options="sortArrayByKey(filteredUsers || [], 'name')"
      optionLabel="name"
      :show-clear="true"
      placeholder="Selecteer gebruiker"
      :disabled="!editAllowed || disabled"
      filter
    />
    <label :for="'select-user'">Gebruiker</label>
  </IftaLabel>
</template>
