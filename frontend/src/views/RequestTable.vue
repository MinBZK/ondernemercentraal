<script setup lang="ts">
import type { components } from '@/api/schema'
import { sortArrayByKey } from '@/util'

import { PrimeIcons } from '@primevue/core/api'

type Request = components['schemas']['Request']

const props = withDefaults(
  defineProps<{
    caseId: string
    showCaseNumber?: boolean
  }>(),
  {
    showCaseNumber: false,
  },
)

const caseId = toRef(props, 'caseId')

const { fetch: fetchRequests, deleteRequest, requests } = useRequest(caseId)
fetchRequests()

const { requestLabels } = useEntityLabels()

const tableConfig: TableColumnConfig<Request>[] = [
  {
    key: 'name',
    label: requestLabels['name'],
  },
  { key: 'form', label: requestLabels.form, dataType: 'custom' },
  { key: 'form_is_completed', label: requestLabels.form_is_completed, dataType: 'boolean' },
  {
    key: 'form_status',
    dataType: 'text',
    label: requestLabels.form_status,
  },
  {
    key: 'updated_at',
    label: requestLabels['updated_at'],
    dataType: 'datetime',
  },
]

const { me } = useAuth()
const showCrud = ref(false)
const selectedRequest = ref<Request>()

type ContextMenuActions = 'Bewerken' | 'Verwijderen'

const menuItems: ContextMenuItem<ContextMenuActions>[] = [
  {
    icon: PrimeIcons.FILE_EDIT,
    label: 'Bewerken',
    hide: !(
      me.value?.permissions.includes('task:update') ||
      me.value?.permissions.includes('task:update:completion-status')
    ),
  },
  {
    icon: PrimeIcons.TRASH,
    label: 'Verwijderen',
    hide: !me.value?.permissions.includes('task:delete'),
  },
]

const { askToConfirm } = useConfirm()

const showFormCrud = ref(false)
watch(showFormCrud, () => {
  if (!showFormCrud.value) {
    selectedRequest.value = undefined
  }
})
</script>

<template>
  <Dialog
    v-model:visible="showCrud"
    header="Aanvraag"
    :modal="true"
    :dismissable-mask="true"
    @update="selectedRequest = undefined"
  >
    <RequestCrud
      :request-id="selectedRequest?.id"
      :case-id="caseId"
      @update="[(showCrud = false), (selectedRequest = undefined), fetchRequests()]"
    />
  </Dialog>
  <div>
    <Button
      v-if="me?.permissions.includes('request:create')"
      @click="showCrud = true"
      size="small"
      :variant="'outlined'"
      :icon="PrimeIcons.PLUS"
      label="Aanvraag"
    />
  </div>

  <OcTable
    :data="sortArrayByKey([...requests], 'name')"
    :table-config="tableConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #custom="{ row: currentRow }">
      <router-link
        :to="{
          name: 'BeheerRequestFormData',
          params: {
            requestId: currentRow.id,
            formDataId: currentRow.form.id,
          },
        }"
      >
        <Button
          label="Bekijk formulier"
          size="small"
          class="mr-2"
          :variant="'outlined'"
          :icon="PrimeIcons.WINDOW_MAXIMIZE"
        />
      </router-link>
    </template>
    <template #action="{ row: currentRow }">
      <ContextMenu
        :menu-items="menuItems"
        @item-clicked="
          async (item) => {
            if (item.label === 'Verwijderen') {
              await askToConfirm({
                question: `Weet je zeker dat je deze taak wilt verwijderen?`,
                title: 'Taak verwijderen',
              })
              await deleteRequest(currentRow.id)
              fetchRequests()
            } else if (item.label === 'Bewerken') {
              selectedRequest = currentRow
              showCrud = true
            }
          }
        "
      />
    </template>
  </OcTable>
  <DialogForm
    v-if="selectedRequest"
    :form-template-name="selectedRequest.form.form_template_name"
    :form-title="selectedRequest.form.form_template_name"
    :request-id="selectedRequest.id"
    :form-data-id="selectedRequest.form.id"
    @submit="fetchRequests()"
    v-model="showFormCrud"
  />
</template>
