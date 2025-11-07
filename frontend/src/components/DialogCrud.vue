<script setup lang="ts">
withDefaults(
  defineProps<{
    header: string
    useWideMode?: boolean
    dismissableMask?: boolean
  }>(),
  {
    useWideMode: false,
    dismissableMask: true,
  },
)

const show = defineModel({
  default: true,
})

const containerElement = useTemplateRef('container')
onMounted(() => {
  containerElement.value?.focus()
})

const emit = defineEmits<{
  close: []
}>()

const { navigateToParentRoute } = useParentRoute()
</script>

<template>
  <Dialog
    v-model:visible="show"
    :header="header"
    :modal="true"
    :dismissable-mask="dismissableMask"
    :style="useWideMode ? { width: '100%' } : null"
    :class="useWideMode ? 'max-w-[1200px]' : 'min-w-2xl'"
    :position="useWideMode ? 'top' : 'center'"
    @hide="[navigateToParentRoute(), emit('close')]"
  >
    <div class="flex flex-col max-h-[calc(100vh-200px)]">
      <div
        class="flex-1 overflow-y-auto overflow-x-hidden"
        ref="container"
        id="dialog-content-container"
      >
        <slot />
      </div>
      <div class="mt-4 text-right"><slot name="actions" /></div>
    </div>
  </Dialog>
</template>

<style scoped>
:deep(.p-dialog-content) {
  padding: 0 !important;
}
</style>
