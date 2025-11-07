import type { components } from '@/api/schema'

type Comment = components['schemas']['Comment']

const { client } = useApiClient()

export function useComment(
  caseId: Ref<string | undefined>,
  trackId: Ref<string | undefined>,
  appointmentId: Ref<string | undefined>,
) {
  const comments = ref<Comment[]>([])

  async function fetchMany() {
    const { data } = await client.GET('/api/comment/', {
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
    comments.value = data
  }

  async function createComment(content: string) {
    return client.POST('/api/comment/', {
      params: {
        query: {
          content,
          case_id: caseId.value || null,
          track_id: trackId.value || null,
          appointment_id: appointmentId.value || null,
        },
      },
    })
  }

  return { comments, fetchMany, createComment }
}
