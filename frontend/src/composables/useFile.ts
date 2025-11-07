import type { components } from '@/api/schema'

type FileBase = components['schemas']['FileBase']

const { client } = useApiClient()

export function useFile(
  caseId: Ref<string | undefined>,
  trackId: Ref<string | undefined>,
  appointmentId: Ref<string | undefined>,
) {
  const files = ref<FileBase[]>()

  async function fetchMany() {
    const { data } = await client.GET('/api/file/', {
      params: {
        query: {
          case_id: caseId.value || null,
          track_id: trackId.value || null,
          appointment_id: appointmentId.value || null,
        },
      },
    })
    if (!data) {
      throw new Error('No data returned from API')
    }
    files.value = data
  }

  async function updateFile(fileUpdate: components['schemas']['FileUpdate'], fileId: string) {
    return client.PUT('/api/file/{file_id}', {
      body: fileUpdate,
      params: {
        path: {
          file_id: fileId,
        },
        query: {
          case_id: caseId.value || null,
          track_id: trackId.value || null,
          appointment_id: appointmentId.value || null,
        },
      },
    })
  }

  async function deleteFile(fileId: string) {
    return client.DELETE('/api/file/{file_id}', {
      params: {
        path: {
          file_id: fileId,
        },
        query: {
          case_id: caseId.value || null,
          track_id: trackId.value || null,
          appointment_id: appointmentId.value || null,
        },
      },
    })
  }

  return { files, fetchMany, updateFile, deleteFile }
}
