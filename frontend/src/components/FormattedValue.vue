<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'
import { formatDateOrTimeLike } from '@/util/format'

const props = defineProps<{
  value: string | number | Date | null | undefined | boolean
  dataType: DataType
  title?: string
}>()

const maxLength = 150

const displayedValue = computed(() =>
  typeof props.value === 'string' && props.value.length > maxLength
    ? props.value.slice(0, maxLength)
    : props.value,
)

const hasShortenedValue = computed(
  () =>
    typeof displayedValue.value == 'string' &&
    typeof props.value == 'string' &&
    displayedValue.value.length != props.value.length,
)

const showFullContent = ref<boolean>(false)

const dateLikeDataTypes: DataType[] = ['date', 'date-long', 'datetime', 'relative-datetime', 'time']
</script>

<template>
  <template v-if="value === null || value === undefined">
    {{ value }}
  </template>

  <template v-if="dateLikeDataTypes.includes(dataType) && typeof value == 'string'">
    <span class="nowrap">{{ formatDateOrTimeLike(value, dataType as DataTypeDateLike) }}</span>
  </template>

  <!-- <template v-if="dataType == 'date' && typeof value == 'string'">
    <span class="nowrap">{{ formatUtcDate(value, 'short') }}</span>
  </template>
  <template v-else-if="dataType == 'date-long' && typeof value == 'string'">
    <span class="nowrap">{{ formatUtcDate(value, 'longDate') }}</span>
  </template>
  <template v-else-if="dataType == 'datetime' && typeof value == 'string'">
    <span class="nowrap">{{ formatUtcDate(value, 'long') }}</span>
  </template>
  <template v-else-if="dataType == 'relative-datetime' && typeof value == 'string'">
    <span class="nowrap">{{ formatUtcDateRelative(value) }}</span>
  </template>
  <template v-else-if="dataType == 'time' && typeof value == 'string'">
    <span class="nowrap">{{ formatUtcDate(value, 'time') }}</span>
  </template> -->

  <template v-else-if="dataType == 'boolean'">
    <i
      :class="value ? ['text-green-500', PrimeIcons.CHECK] : ['text-orange-300', PrimeIcons.TIMES]"
    />
  </template>
  <template v-else>
    {{ displayedValue }}{{ hasShortenedValue ? '...' : '' }}
    <i
      v-if="hasShortenedValue"
      :class="PrimeIcons.SEARCH"
      class="inline-icon"
      @click="showFullContent = true"
    />
  </template>
  <Dialog v-model:visible="showFullContent" modal :header="title" :dismissable-mask="true">
    {{ value }}
  </Dialog>
</template>

<style scoped>
.inline-icon {
  font-size: 0.75em;
  font-weight: bold;
  color: var(--primary);
  cursor: pointer;
}

.inline-icon:hover {
  color: var(--secondary);
}

:deep(.p-dialog-content) {
  line-height: 2em;
}

.nowrap {
  white-space: nowrap;
}
</style>
