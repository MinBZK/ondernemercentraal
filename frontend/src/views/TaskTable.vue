<script setup lang="ts">
import type { components } from '@/api/schema'
import { sortArrayByKey } from '@/util'

import { PrimeIcons } from '@primevue/core/api'

type Task = components['schemas']['Task']

const props = withDefaults(
  defineProps<{
    showCaseNumber?: boolean
    caseId?: string
  }>(),
  {
    showCaseNumber: false,
  },
)

const caseId = toRef(props, 'caseId')
const { fetch: fetchTasks, deleteTask, tasks } = useTask(undefined, caseId)
fetchTasks()

const { taskLabels } = useEntityLabels()

const tableConfig: TableColumnConfig<Task>[] = [
  {
    key: 'case_number',
    label: taskLabels.case_number,
    hide: !props.showCaseNumber,
    dataType: 'custom',
  },
  {
    key: 'description',
    label: taskLabels['description'],
  },
  {
    key: 'due_date',
    label: taskLabels['due_date'],
    dataType: 'date',
  },
  {
    key: 'status',
    label: taskLabels['status'],
    dataType: 'text',
  },
  {
    key: 'completed',
    label: taskLabels['completed'],
    dataType: 'boolean',
  },
  {
    key: 'user_name',
    label: taskLabels.user_name,
    dataType: 'text',
  },
  {
    key: 'updated_at',
    label: taskLabels['updated_at'],
    dataType: 'datetime',
  },
]

const { me } = useAuth()
const showCrud = ref(false)
const selectedTask = ref<Task>()

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

watch(showCrud, (newValue) => {
  if (!newValue) {
    selectedTask.value = undefined
  }
})
</script>

<template>
  <Dialog
    v-model:visible="showCrud"
    header="Taak"
    :modal="true"
    :dismissable-mask="true"
    @update="selectedTask = undefined"
  >
    <TaskCrud
      :task-id="selectedTask?.id"
      :case-id="caseId"
      @update="[(showCrud = false), (selectedTask = undefined), fetchTasks()]"
    />
  </Dialog>
  <div>
    <Button
      v-if="me?.permissions.includes('task:create')"
      @click="showCrud = true"
      size="small"
      :variant="'outlined'"
      :icon="PrimeIcons.PLUS"
      label="Taak"
    />
  </div>

  <OcTable
    :data="sortArrayByKey([...tasks], 'due_date')"
    :table-config="tableConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #custom="{ column, row }">
      <router-link
        v-if="column.key == 'case_number'"
        :to="{
          name: 'BeheerCaseDetail',
          params: { caseId: row.case.id },
        }"
        >{{ row.case_number }}</router-link
      >
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
              await deleteTask(currentRow.id)
              fetchTasks()
            } else if (item.label === 'Bewerken') {
              selectedTask = currentRow
              showCrud = true
            }
          }
        "
      />
    </template>
  </OcTable>
</template>
