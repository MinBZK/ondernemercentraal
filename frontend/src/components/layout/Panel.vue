<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'

const props = withDefaults(
  defineProps<{
    expandedByDefault: boolean
    title: string
    nCols?: 1 | 2 | 3 | 4 | 5 | 6
    expandable?: boolean
  }>(),
  {
    expandedByDefault: false,
    nCols: 4,
    expandable: true,
  },
)

const expanded = ref<boolean>(props.expandedByDefault)
</script>

<template>
  <div class="border-solid border border-quaternary mb-6 rounded-md p-3">
    <div
      :class="['grid grid-cols-4', expandable && 'expand-row unselectable']"
      @click="expandable ? (expanded = !expanded) : null"
    >
      <div class="col-span-3 mb-0">
        <h2 class="m-0">
          {{ props.title }}
        </h2>
      </div>
      <div class="col-span-1 text-right mb-0">
        <i
          v-if="expandable"
          :class="expanded ? PrimeIcons.CHEVRON_DOWN : PrimeIcons.CHEVRON_UP"
          class="expand-icon"
        />
      </div>
    </div>

    <div v-if="expanded" class="pt-2">
      <div class="col-span-full text-left pb-2 slot-container">
        <slot name="actions-top" />
      </div>

      <slot />
      <div class="col-span-full text-left py-2 slot-container">
        <slot name="actions-bottom" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.p-panel {
  border: 0;
}

.expand-row {
  cursor: pointer;
}

.expand-icon {
  font-size: 1em;
  font-weight: bold;
  padding: 0.25em;
}

.unselectable {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* IE 10+ */
  user-select: none; /* Standard syntax */
}

h2 {
  font-size: 1.3em;
}

.slot-container:empty {
  padding: 0;
}
</style>
