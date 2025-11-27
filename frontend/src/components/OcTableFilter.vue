<script lang="ts">
export const selectNoneString = '__NULL__'
</script>

<script setup lang="ts" generic="T extends Record<string, TableValue>">
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  tableColumnConfig: TableColumnConfig<T>
  values: TableValue[]
}>()
const selectedValues = defineModel<TableValue[]>('selectedValues', { default: () => [] })
const label = computed(() => props.tableColumnConfig.label())

const showFilter = defineModel<boolean>('showFilter', { default: true })
const emit = defineEmits<{
  close: []
  updateFilterValues: TableValue[]
}>()

watch(showFilter, (newValue) => {
  if (!newValue) {
    emit('close')
  }
})

type FilterValue = {
  value: TableValue
  stringifiedValue: string
}

const stringifiedValue = (v: TableValue) => {
  if (props.tableColumnConfig.stringifiedValueKey && v) {
    return v[props.tableColumnConfig.stringifiedValueKey]
  } else if (props.tableColumnConfig.stringifiedValueKey) {
    return '(geen)'
  } else if (v) {
    return v.toString()
  } else {
    return '(geen)'
  }
}

const uniqueSortedValues = computed(() => [...new Set(props.values)].sort())

const enrichedValues = computed((): FilterValue[] => {
  return uniqueSortedValues.value.map((v) => {
    return {
      value: v || selectNoneString,
      stringifiedValue: stringifiedValue(v),
    }
  })
})

function handleApplyFilter() {
  showFilter.value = false
  emit('updateFilterValues', selectedValues.value)
}
</script>

<template>
  <Dialog v-model:visible="showFilter" modal :header="label" :dismissable-mask="true">
    <div class="max-h-[300px] overflow-y-auto max-w-[300px]">
      <div
        v-for="v in enrichedValues"
        :key="v.stringifiedValue"
        class="flex items-center gap-2 my-2"
      >
        <Checkbox
          v-model="selectedValues"
          :inputId="v.stringifiedValue"
          name="dynamic"
          :value="v.value"
        />
        <label :for="v.stringifiedValue" class="cursor-pointer">
          <FormattedValue
            :value="v.stringifiedValue"
            :data-type="tableColumnConfig.dataType || 'text'"
          />
        </label>
      </div>
    </div>
    <Divider />
    <div v-if="selectedValues.length > 0" class="pb-2 text-sm">
      {{ selectedValues.length }}
      {{ selectedValues.length == 1 ? 'waarde' : 'waardes' }} geselecteerd
    </div>
    <div class="flex grid grid-cols-2 gap-3">
      <div>
        <Button
          label="Selecteer alles"
          class="w-full"
          variant="outlined"
          size="small"
          :icon="PrimeIcons.CHECK"
          @click="selectedValues = values"
          :disabled="selectedValues.length === values.length"
        />
      </div>
      <div>
        <Button
          label="Verwijder selectie"
          :icon="PrimeIcons.TIMES"
          class="w-full"
          @click="selectedValues = []"
          variant="outlined"
          size="small"
          :disabled="selectedValues.length === 0"
        />
      </div>
    </div>
    <Divider />
    <Button label="Filter toepassen" class="w-full" @click="handleApplyFilter" />
  </Dialog>
</template>
