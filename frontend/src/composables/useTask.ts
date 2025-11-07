import type { components } from '@/api/schema'

const { client: ApiClient } = useApiClient()

export function useTask(taskId?: Ref<string | undefined>, caseId?: Ref<string | undefined>) {
  const tasks = ref<components['schemas']['Task'][]>([])

  async function fetch() {
    const { data } = await ApiClient.GET('/api/task/', {
      params: {
        query: {
          case_id: caseId?.value,
        },
      },
    })
    if (!data) {
      throw new Error('Failed to fetch tasks')
    }
    tasks.value = data
  }

  const assertedTaskId = computed(() => {
    if (!taskId?.value) {
      throw new Error('Task ID is required')
    }
    return taskId.value
  })

  function updateTask(payload: components['schemas']['TaskUpsert']) {
    return ApiClient.PUT('/api/task/{task_id}', {
      params: {
        path: {
          task_id: assertedTaskId.value,
        },
      },
      body: payload,
    })
  }

  function createTask(payload: components['schemas']['TaskUpsert']) {
    return ApiClient.POST('/api/task/', { body: payload })
  }

  function deleteTask(taskId: string) {
    return ApiClient.DELETE('/api/task/{task_id}', {
      params: {
        path: {
          task_id: taskId,
        },
      },
    })
  }

  return {
    tasks,
    fetch,
    updateTask,
    createTask,
    deleteTask,
  }
}
