<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

import { sortArrayByKey } from '@/util'

const { users, fetchMany, deleteUser, resetPassword } = useUser()
const { notify } = useNotification()
const { askToConfirm } = useConfirm()
const { me } = useAuth()

fetchMany()

type userTableConfig = TableColumnConfig<components['schemas']['User']>

const userTableConfig: userTableConfig[] = [
  {
    key: 'name',
    label: () => 'Naam',
  },
  {
    key: 'role_name',
    label: () => 'Rol',
    dataType: 'text',
  },
  {
    key: 'partner_organization_name',
    label: () => 'Partnerorganisatie',
    dataType: 'text',
  },
  {
    key: 'active',
    label: () => 'Actief',
    dataType: 'boolean',
  },
  {
    key: 'updated_at',
    label: () => 'Gewijzigd op',
    dataType: 'datetime',
  },
]

const showUserCrud = ref(false)
const selectedUser = ref<components['schemas']['User']>()

type ContextMenuActions = 'Bewerken' | 'Verwijderen' | 'Reset wachtwoord'

const menuItems: ContextMenuItem<ContextMenuActions>[] = [
  {
    icon: PrimeIcons.FILE_EDIT,
    label: 'Bewerken',
  },
  {
    icon: PrimeIcons.REFRESH,
    label: 'Reset wachtwoord',
    hide: !me.value?.permissions.includes('user:update'),
  },
  {
    icon: PrimeIcons.TRASH,
    label: 'Verwijderen',
    hide: !me.value?.permissions.includes('user:delete'),
  },
]

function handleDelete(targetUser: components['schemas']['User']) {
  return askToConfirm({
    question: `Weet je zeker dat je de gebruiker '${targetUser.name}' wilt verwijderen?`,
    title: 'Gebruiker verwijderen',
  }).then(async () => {
    await deleteUser(targetUser.id)
    selectedUser.value = undefined
    fetchMany()
  })
}

function handleEdit(targetUser: components['schemas']['User']) {
  selectedUser.value = targetUser
  showUserCrud.value = true
}

async function handleResetPassword(targetUser: components['schemas']['User']) {
  const { password } = await resetPassword(targetUser.id)
  notify({
    message: `Het wachtwoord van gebruiker '${targetUser.name}' is gereset. Het nieuwe wachtwoord is: ${password}`,
  })
}
</script>

<template>
  <Page page-title="Gebruikers">
    <Dialog
      v-model:visible="showUserCrud"
      header="Gebruiker"
      :modal="true"
      :dismissable-mask="true"
      @update:visible="selectedUser = undefined"
    >
      <UserCrud @submit="[fetchMany(), (showUserCrud = false)]" :user="selectedUser" />
    </Dialog>
    <Button
      :icon="PrimeIcons.PLUS"
      size="small"
      outlined
      @click="showUserCrud = true"
      label="Aanmaken"
    />
    <OcTable
      :data="sortArrayByKey(users, 'name')"
      :table-config="userTableConfig"
      :id-key="'id'"
      :show-action-column="true"
    >
      <template #custom="{ row: user }">
        <BeheerSelectRole v-model="user.role" />
      </template>
      <template #action="{ row: currentUser }">
        <ContextMenu
          :menu-items="menuItems"
          @item-clicked="
            (item) => {
              if (item.label === 'Bewerken') {
                handleEdit(currentUser)
              } else if (item.label === 'Verwijderen') {
                handleDelete(currentUser)
              } else if (item.label == 'Reset wachtwoord') {
                handleResetPassword(currentUser)
              }
            }
          "
        />
      </template>
    </OcTable>
  </Page>
</template>
