<script setup lang="ts" generic="T extends string">
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  menuItems: ContextMenuItem<T>[]
}>()

const emit = defineEmits<{
  'item-clicked': [ContextMenuItem<T>]
}>()

const popover = useTemplateRef('contextMenu')

const visibleMenuItems = computed(() => {
  return props.menuItems.filter((item) => !item.hide)
})
</script>

<template>
  <Button
    :icon="PrimeIcons.ELLIPSIS_V"
    size="small"
    outlined
    @click="(e) => popover?.toggle(e)"
    v-if="visibleMenuItems.length > 0"
  />
  <Popover ref="contextMenu">
    <ul>
      <li
        class="cursor-pointer text-sm/10 hover:bg-primary/10 rounded-lg px-2 text-primary"
        v-for="item in visibleMenuItems"
        :key="item.label"
        @click="emit('item-clicked', item)"
      >
        <i :class="['mr-2', item['icon']]" />{{ item['label'] }}
      </li>
    </ul>
  </Popover>
</template>
