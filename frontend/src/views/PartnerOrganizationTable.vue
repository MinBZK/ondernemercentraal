<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'
import { sortArrayByKey } from '@/util'

const {
  partnerOrganizations,
  fetch: fetchPartnerOrganizations,
  deletePartnerOrganization,
} = usePartnerOrganization()
const { partnerOrganizationLabels } = useEntityLabels()
fetchPartnerOrganizations()

const { me } = useAuth()
const showCrud = ref(false)

type PartnerOrganization = components['schemas']['PartnerOrganization']

const partnerOrganizationConfig: TableColumnConfig<PartnerOrganization>[] = [
  {
    key: 'name',
    label: partnerOrganizationLabels.name,
  },
  {
    key: 'product_names',
    label: partnerOrganizationLabels.product_names,
    dataType: 'string-list',
  },
  {
    key: 'created_at',
    label: partnerOrganizationLabels.created_at,
    dataType: 'datetime',
  },
]

const selectedPartnerOrganization = ref<PartnerOrganization>()

type ContextMenuActions = 'Bewerken' | 'Verwijderen'

const menuItems: ContextMenuItem<ContextMenuActions>[] = [
  {
    icon: PrimeIcons.FILE_EDIT,
    label: 'Bewerken',
    hide: !me.value?.permissions.includes('partner-organization:update'),
  },
  {
    icon: PrimeIcons.TRASH,
    label: 'Verwijderen',
    hide: !me.value?.permissions.includes('partner-organization:delete'),
  },
]
</script>

<template>
  <Dialog
    v-model:visible="showCrud"
    header="Partnerorganisatie"
    :modal="true"
    :dismissable-mask="true"
    @update="selectedPartnerOrganization = undefined"
  >
    <PartnerOrganizationCrud
      :partner-organization-id="selectedPartnerOrganization?.id"
      @update="[
        (showCrud = false),
        (selectedPartnerOrganization = undefined),
        fetchPartnerOrganizations(),
      ]"
    />
  </Dialog>
  <Button
    v-if="me?.permissions.includes('partner-organization:create')"
    @click="showCrud = true"
    size="small"
    :variant="'outlined'"
    :icon="PrimeIcons.PLUS"
    label="Partnerorganisatie"
  />
  <OcTable
    :data="sortArrayByKey(partnerOrganizations, 'name')"
    :table-config="partnerOrganizationConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #action="{ row: currentPc }">
      <ContextMenu
        :menu-items="menuItems"
        @item-clicked="
          async (item) => {
            if (item.label === 'Verwijderen') {
              await deletePartnerOrganization(currentPc.id)
              fetchPartnerOrganizations()
            } else if (item.label === 'Bewerken') {
              selectedPartnerOrganization = currentPc
              showCrud = true
            }
          }
        "
      />
    </template>
  </OcTable>
</template>
