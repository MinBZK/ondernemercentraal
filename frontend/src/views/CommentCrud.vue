<script setup lang="ts">
export type CommentCrudProps = {
  caseId?: string
  trackId?: string
  appointmentId?: string
}

const props = defineProps<CommentCrudProps>()

const caseId = toRef(props, 'caseId')
const trackId = toRef(props, 'trackId')
const appointmentId = toRef(props, 'appointmentId')
const {
  comments,
  fetchMany: fetchComments,
  createComment,
} = useComment(caseId, trackId, appointmentId)
fetchComments()

async function handleCreateComment() {
  await createComment(comment.value)
  comment.value = ''
  fetchComments()
}

const comment = ref<string>('')

const page = ref(1)
const first = ref(0)
const limit = 5
const paginatedComments = computed(() => comments.value.slice(first.value, first.value + limit))
</script>

<template>
  <Textarea
    v-model="comment"
    class="w-2xl"
    :placeholder="'Schrijf een notitie'"
    @keydown.enter.ctrl="handleCreateComment"
  >
    Hoi
  </Textarea>
  <div>
    <Button label="Opslaan" @click="handleCreateComment"></Button>
  </div>
  <Divider />

  <div class="space-y-4 py-4">
    <div v-for="(msg, index) in paginatedComments" :key="index" class="flex flex-col">
      <!-- Name and time -->
      <div class="text-xs text-gray-500 mb-1">
        {{ msg.created_by_user.name }} op
        <span><FormattedValue :value="msg.created_at" :data-type="'datetime'" /></span>
      </div>

      <!-- Chat bubble -->
      <div class="px-4 py-2 rounded-2xl max-w-[75%]" :class="'bg-gray-200 self-start'">
        {{ msg.content }}
      </div>
    </div>
    <Paginator
      :rows="limit"
      :total-records="comments.length"
      v-model:first="first"
      :always-show="false"
      @page="({ page: newPage }) => (page = newPage)"
    >
      <template #end>
        <span v-if="comments.length > limit" class="text-secondary">
          Notitie {{ first + 1 }} -
          {{ first + limit > comments.length ? comments.length : first + limit }}
          van {{ comments.length }}
        </span>
      </template>
    </Paginator>
  </div>
</template>
