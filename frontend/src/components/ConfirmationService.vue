<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm'

const { confirmationQuery, confirm, cancel } = useConfirm()

const visible = ref<boolean>(false)

const message = ref<string>('')

watch(confirmationQuery, () => {
  visible.value = Boolean(confirmationQuery)
})
</script>

<template>
  <Dialog
    v-if="confirmationQuery"
    v-model:visible="visible"
    modal
    :header="confirmationQuery.title"
    :style="{ width: '35rem' }"
    :dismissable-mask="true"
  >
    {{ confirmationQuery?.question }}

    <div v-if="confirmationQuery.requireUserMessage" class="flex align-items-center gap-3 my-3">
      <Textarea v-model="message" rows="5" cols="60" />
    </div>
    <Tag v-if="confirmationQuery.isMessageRequired" severity="danger" value="Verplicht veld" />
    <div class="flex justify-end gap-2 mt-3">
      <Button
        type="button"
        label="Annuleren"
        outlined
        @click="[cancel(), (visible = false), (message = '')]"
      />
      <Button
        type="button"
        label="Bevestigen"
        :disabled="confirmationQuery.isMessageRequired && !message"
        @click="[confirm(message), (visible = false), (message = '')]"
      />
    </div>
  </Dialog>
</template>
