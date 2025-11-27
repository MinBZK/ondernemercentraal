<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  taskId?: string
  caseId?: string
}>()

const taskId = toRef(props, 'taskId')
const { taskLabels } = useEntityLabels()
const { createTask, updateTask, fetch: fetchTasks, tasks } = useTask(taskId)

fetchTasks()

const task = computed(() => tasks.value.find((t) => t.id === taskId.value))

const taskConfig = computed((): FormField<components['schemas']['Task']>[] => {
  return [
    {
      key: 'description',
      label: () => taskLabels.description(),
      type: 'text',
      optional: false,
      readOnly: !me.value?.permissions.includes('task:update'),
    },
    {
      key: 'due_date',
      label: () => taskLabels.due_date(),
      type: 'date',
      optional: false,
      readOnly: !me.value?.permissions.includes('task:update'),
    },
    {
      key: 'status',
      label: () => taskLabels.status(),
      type: 'select',
      optional: false,

      options: ['Openstaand', 'In uitvoering', 'Gesloten'],
      readOnly: !me.value?.permissions.includes('task:update'),
    },
    {
      key: 'case_id',
      label: () => taskLabels.case_id(),
      type: 'custom',
      optional: false,
      readOnly: !me.value?.permissions.includes('task:update'),
    },
    {
      key: 'user_id',
      label: () => taskLabels.user_name(),
      type: 'custom',
      optional: true,
      readOnly: !me.value?.permissions.includes('task:update'),
    },
    {
      key: 'completed',
      label: () => taskLabels.completed(),
      type: 'checkbox',
      optional: true,
      readOnly: !me.value?.permissions.includes('task:update:completion-status'),
    },
  ]
})

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const taskCreate = schemas.TaskUpsert.strict()

  // pre-process the state: Zod expects a string while it actually is and should be a Date
  const preprocessedState = { ...state }
  //@ts-expect-error fix wrong Zod schema/type
  preprocessedState.due_date = preprocessedState.due_date.toISOString()
  preprocessedState.completed = Boolean(preprocessedState.completed)
  preprocessedState.user_id = preprocessedState.user_id || null

  const parsedPayload = taskCreate.parse(preprocessedState)
  if (!taskId.value) {
    await createTask(parsedPayload)
  } else {
    await updateTask(parsedPayload)
  }
  emit('update')
}

const { me } = useAuth()
const formIsValid = ref(false)

type TaskStateFormState = Record<keyof components['schemas']['TaskUpsert'], unknown>

const state: TaskStateFormState = reactive({
  user_id: undefined,
  case_id: undefined,
  description: '',
  due_date: undefined,
  status: undefined,
  completed: undefined,
})

const selectedCase = ref<components['schemas']['CaseBase']>()
const selectedUser = ref<components['schemas']['UserBase']>()
watch(
  task,
  () => {
    selectedCase.value = task.value?.case
    selectedUser.value = task.value?.user || undefined
  },
  { immediate: true },
)

watch(
  selectedCase,
  (newCase) => {
    state.case_id = newCase?.id
  },
  { immediate: true },
)

watch(
  selectedUser,
  (newUser) => {
    state.user_id = newUser?.id
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <FormFieldList
    :form-field-config="taskConfig"
    :data="task"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(state, formStateValues)
        formIsValid = isValid
      }
    "
    :n-columns="1"
  >
    <template #after="{ field }">
      <BeheerSelectCase
        :initial-case-id="task?.case_id || caseId"
        :read-only="Boolean(caseId)"
        v-model="selectedCase"
        class="w-full"
        v-if="field.key == 'case_id'"
      />
      <BeheerSelectUser
        :initial-user-id="task?.user_id || undefined"
        v-model="selectedUser"
        :case-id="selectedCase?.id"
        :disabled="!me?.permissions.includes('task:update')"
        class="w-full"
        v-if="field.key == 'user_id'"
      />
    </template>
  </FormFieldList>

  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    :disabled="!formIsValid || !selectedCase"
    v-if="
      me?.permissions.includes('task:create') ||
      me?.permissions.includes('task:update') ||
      me?.permissions.includes('task:update:completion-status')
    "
  />
</template>
