<script setup lang="ts" generic="T extends Record<string, any>">
import { sortArrayByKey } from '@/util'
import type { PaginatorPassThroughOptions } from 'primevue/paginator'
import { PrimeIcons } from '@primevue/core/api'
import { selectNoneString } from './OcTableFilter.vue'

const props = withDefaults(
  defineProps<{
    data: T[]
    idKey: keyof T
    nameKey?: keyof T | null
    tableConfig: TableColumnConfig<T>[]
    limit?: number
    rowCount?: number
    dataIsAlreadyPaginated?: boolean
    nArrayItemsToDisplay?: number
    showSearchBar?: boolean
    showActionColumn?: boolean
    rowLinkConfig?: RowLinkConfig<T>
  }>(),
  {
    limit: 10,
    dataIsAlreadyPaginated: false,
    nArrayItemsToDisplay: 3,
    showSearchBar: true,
    nameKey: null,
    showActionColumn: false,
  },
)

if (!props.rowCount && props.dataIsAlreadyPaginated) {
  throw new Error('rowCount is required when dataIsAlreadyPaginated is true')
}

const rowCountFinal = computed(() => props.rowCount || props.data.length)

const page = defineModel<number>('page', { default: 1 })
const searchQuery = defineModel<string>('searchQuery', { default: '' })

const buttonClass =
  'py-2 px-4 border-0 text-lg my-3 mx-1 bg-tertiary hover:bg-secondary text-primary-dark cursor-pointer pagination-button'

const buttonClassDefault = `${buttonClass} bg-tertiary`
const buttonClassCurrent = `${buttonClass} bg-primary`

const pt: PaginatorPassThroughOptions = {
  current: {
    class: [buttonClassCurrent],
  },
  page: {
    class: [buttonClassDefault],
  },
  first: {
    class: [buttonClassDefault],
  },
  prev: {
    class: [buttonClassDefault],
  },
  last: {
    class: [buttonClassDefault],
  },
  next: {
    class: [buttonClassDefault],
  },
}

const minIndex = computed(() => (page.value - 1) * props.limit)
const maxIndex = computed(() => {
  const max = page.value * props.limit
  return rowCountFinal.value < max ? rowCountFinal.value : max
})

function getStringifiedValue(row: T, tC: TableColumnConfig<T>) {
  // returns a stringified value for a column, which can be used for filtering/searching
  const rowValue = row[tC.key]
  let stringValue = ''
  const columnKey = tC.key.toString()
  const stringifiedValueKey = tC.stringifiedValueKey
  const isDateOrTime =
    tC.dataType === 'date' ||
    tC.dataType === 'datetime' ||
    tC.dataType == 'time' ||
    tC.dataType == 'date-long'
  if (stringifiedValueKey) {
    stringValue = rowValue?.[stringifiedValueKey] || ''
    if (typeof stringValue !== 'string') {
      console.error('Stringified value', stringValue)
      throw new Error(
        `The stringified value for key '${stringifiedValueKey.toString()}' for column '${columnKey}' does not return a string, but '${typeof stringValue}'`,
      )
    }
  } else if (typeof rowValue == 'string') {
    stringValue = rowValue.toLowerCase()
  } else if (typeof rowValue == 'number') {
    stringValue = rowValue.toString().toLowerCase()
  } else if (typeof rowValue == 'object' && isDateOrTime) {
    stringValue = ''
  } else {
    console.info(
      `Column ${columnKey} has no string value, cannot filter by search query. The value is ${rowValue}, the type is: ${typeof rowValue}`,
    )
  }
  return stringValue
}

// function filterValueMatchesRowValue(filterValue: TableValue, value: T[keyof T]) {
//   return
// }

function getStringifiedValueKey(filterKey: keyof T) {
  const tableColumnConfig = props.tableConfig.find((tC) => tC.key === filterKey)
  const stringifiedValueKey = tableColumnConfig?.stringifiedValueKey
  return stringifiedValueKey
}

function applyFilters(filters: TableFilter[], data: T[]) {
  const filteredData = filters.reduce((acc, filter) => {
    if (filter.values.length > 0) {
      return acc.filter((row) => {
        const rowValue = row[filter.key]

        // If the rowValue is an object, we need to use the stringifiedValueKey to get the value used for filtering
        const stringifiedValueKey = getStringifiedValueKey(filter.key)
        const flatRowValue = stringifiedValueKey ? rowValue?.[stringifiedValueKey] : rowValue

        const flatRowValueIsArray = Array.isArray(flatRowValue)

        const flatFilterValues = filter.values.map((v) => {
          // Replace the filter values that are an object with a stringified value
          const isObjectWithStringifiedValueKey = typeof v === 'object' && stringifiedValueKey

          // Replace the filter value with undefined if it a string equal to 'selectNoneString'
          const replaceNoneString = (v: string) => (v === selectNoneString ? undefined : v)

          return isObjectWithStringifiedValueKey ? v[stringifiedValueKey] : replaceNoneString(v)
        })

        if (flatRowValueIsArray) {
          return flatFilterValues.some((v) => flatRowValue.includes(v))
        } else {
          return flatFilterValues.includes(flatRowValue)
        }
      })
    }
    return acc
  }, data)

  const filteredDataBySearchQuery = filteredData.filter((row) => {
    const stringifiedValues = props.tableConfig.map((tC) => getStringifiedValue(row, tC))

    return stringifiedValues.some(
      (stringifiedValue) =>
        stringifiedValue.includes(searchQuery.value.toLowerCase()) || searchQuery.value.length == 0,
    )
  })

  return filteredDataBySearchQuery
}

const sortedData = computed(() => {
  const rawData = [...props.data]
  const data = sortKey.value ? sortArrayByKey(rawData, sortKey.value) : rawData
  const sortedData = sortOrder.value === 'asc' ? data : data.slice().reverse()
  return sortedData
})

const filteredAndSortedData = computed(() => {
  const filters = tableFilters.value as TableFilter[]
  return applyFilters(filters, sortedData.value)
})

function getFiltersWithoutSpecifiedColumn(specifiedColumn: TableColumnConfig<T>) {
  return tableFilters.value.filter((f) => f.key !== specifiedColumn.key)
}

function filtersForColumn(column: TableColumnConfig<T>) {
  return tableFilters.value.filter((f) => f.key == column.key)
}

const rowCount = computed(() =>
  props.dataIsAlreadyPaginated ? rowCountFinal.value : filteredAndSortedData.value.length,
)

// eslint-disable-next-line
function castRow(row: any) {
  return row as T
}

const paginatedData = computed(() => {
  return props.dataIsAlreadyPaginated
    ? filteredAndSortedData.value
    : filteredAndSortedData.value.slice(minIndex.value, maxIndex.value)
})

const sortKey = ref<keyof T>()

type SortOrder = 'asc' | 'desc'
const defaultSorderOrder: SortOrder = 'asc'
const sortOrder = ref<SortOrder>(defaultSorderOrder)

const handleSort = (key: keyof T) => {
  if (sortKey.value != key) {
    sortKey.value = key
    sortOrder.value = 'asc'
  } else if (sortKey.value === key && sortOrder.value === 'asc') {
    sortOrder.value = 'desc'
  } else {
    sortKey.value = undefined
    sortOrder.value = defaultSorderOrder
  }
}

const { isMobile } = useResponsive()

const showPagination = computed(() => rowCountFinal.value > props.limit)

watch(rowCountFinal, () => {
  // If the current page is not valid anymore because the data has changed, reset the page index to 1
  if (page.value > Math.ceil(rowCountFinal.value / props.limit)) {
    page.value = 1
  }
})

const visibleColumns = computed(() =>
  props.tableConfig.filter((tC) => tC.hide == undefined || !tC.hide),
)

function handleFilter(column: TableColumnConfig<T>) {
  // This function can be used to handle filtering logic when the filter icon is clicked
  selectedColumn.value = column
}

const selectedColumn = ref<TableColumnConfig<T>>()

const filterValues = computed(() => {
  if (!selectedColumn.value) {
    throw new Error('selectedColumn is required for getting filter values')
  }
  const key = selectedColumn.value.key

  const relevantFilters = getFiltersWithoutSpecifiedColumn(selectedColumn.value) as TableFilter[]
  const filteredData = applyFilters(relevantFilters, sortedData.value)

  const values = key ? filteredData.map((row) => row[key]) : []

  return [...new Set(values.flat())]
})

type TableFilter = {
  key: keyof T
  values: TableValue[]
}

const tableFilters = ref<TableFilter[]>([])

function updateFilters(key: keyof T, values: TableValue[]) {
  const existingFilterIndex = tableFilters.value.findIndex((f) => f.key === key)
  const filterExists = existingFilterIndex > -1
  if (filterExists && values.length > 0) {
    tableFilters.value[existingFilterIndex].values = values
  } else if (filterExists && values.length == 0) {
    tableFilters.value.splice(existingFilterIndex, 1)
  } else {
    //@ts-expect-error key has the wrong type somehow
    tableFilters.value.push({ key: key, values })
  }
}

function getSelectedValues(key: keyof T) {
  const filter = tableFilters.value.find((f) => f.key === key)
  return filter ? filter.values : []
}

const selectedValues = ref<TableValue[]>([])
watch(selectedColumn, (newValue) => {
  if (newValue) {
    selectedValues.value = getSelectedValues(newValue.key)
  } else {
    selectedValues.value = []
  }
})

function getRouteParams(row: T) {
  if (!props.rowLinkConfig) {
    throw new Error('rowLinkConfig is undefined')
  }
  const params = props.rowLinkConfig.params.reduce((acc: Record<string, string>, param) => {
    acc[param.routeIdKey] = row[param.idKey]
    return acc
  }, {})
  return params
}
</script>

<template>
  <OcTableFilter
    v-if="selectedColumn"
    :values="filterValues"
    :table-column-config="selectedColumn"
    v-model:selected-values="selectedValues"
    @close="selectedColumn = undefined"
    @update-filter-values="
      (v) => {
        if (!selectedColumn) {
          throw new Error('selectedColumn is undefined when updating filter values')
        }
        updateFilters(selectedColumn.key, v)
      }
    "
  />

  <div class="max-w-full overflow-x-auto">
    <div :class="['grid mt-4', showPagination ? 'grid-cols-2' : 'grid-cols-1']">
      <div v-if="showSearchBar" class="flex mb-4">
        <IconField class="input-container">
          <InputText
            v-model="searchQuery"
            class="border-gray-500"
            placeholder="Zoek in de tabel"
            size="small"
          />
          <InputIcon :class="PrimeIcons.SEARCH" />
        </IconField>
      </div>
      <div v-if="showPagination" :class="['text-gray-400 flex justify-end']">
        {{ minIndex + 1 }}-{{ maxIndex <= rowCount ? maxIndex : rowCount }} van {{ rowCount }}
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th v-if="rowLinkConfig" />
          <th
            v-for="tC in visibleColumns"
            :field="tC.key.toString()"
            :key="tC.key"
            :class="[tC.columnWidth, 'no-wrap']"
          >
            {{ tC.label() }}

            <i
              :class="[
                sortOrder == 'asc' ? PrimeIcons.ARROW_DOWN : PrimeIcons.ARROW_UP,
                'px-0 cursor-pointer hover:text-primary header-icon',
                sortKey == tC.key ? 'visible text-primary' : 'invisible text-gray-400',
              ]"
              @click="handleSort(tC.key)"
              v-if="data.length > 1"
            />
            <i
              :class="[
                PrimeIcons.FILTER,
                filtersForColumn(tC).length > 0
                  ? 'visible text-primary'
                  : 'invisible text-gray-400',
              ]"
              class="px-1 cursor-pointer hover:text-primary text-gray-400 header-icon"
              @click="handleFilter(tC)"
            />
          </th>
          <th v-if="showActionColumn" />
        </tr>
      </thead>
      <tbody>
        <tr v-if="paginatedData.length == 0">
          <td :colspan="tableConfig.length">
            <div class="text-center text-gray-500">Geen resultaten gevonden</div>
          </td>
        </tr>
        <template v-for="row in paginatedData" :key="row[idKey]">
          <tr>
            <td v-if="rowLinkConfig">
              <router-link
                :to="{
                  name:
                    typeof rowLinkConfig.routeName == 'string'
                      ? rowLinkConfig.routeName
                      : rowLinkConfig.routeName(row),
                  params: getRouteParams(row),
                }"
                ><Button :icon="PrimeIcons.ARROW_CIRCLE_RIGHT" size="small" :variant="'outlined'" />
              </router-link>
            </td>
            <td v-for="tC in visibleColumns" :key="tC.key">
              <span :class="(tC.noWrap || tC.dataType == 'datetime') && 'no-wrap'">
                <template v-if="tC.dataType == 'custom'">
                  <slot
                    v-bind="{ column: tC, row: castRow(row) }"
                    :key="castRow(row).Id"
                    name="custom"
                  />
                </template>
                <template v-else-if="tC.dataType == 'string-list'">
                  {{
                    Array.isArray(row[tC.key])
                      ? row[tC.key].slice(0, nArrayItemsToDisplay).join(', ')
                      : ''
                  }}

                  <Tag
                    v-if="row[tC.key].length > nArrayItemsToDisplay"
                    :value="`+${row[tC.key].length - nArrayItemsToDisplay}`"
                    rounded
                  />
                </template>
                <template v-else>
                  <FormattedValue :value="row[tC.key]" :data-type="tC.dataType || 'text'" />
                </template>
              </span>
            </td>
            <td v-if="showActionColumn" class="text-right">
              <slot v-bind="{ row }" name="action" />
            </td>
          </tr>
          <tr v-if="showActionColumn && isMobile"></tr>
        </template>
      </tbody>
    </table>

    <div v-if="showPagination" class="mt-2">
      <div v-if="!isMobile" />
      <div :class="isMobile && 'w-full'">
        <Paginator
          :rows="limit"
          :total-records="rowCount"
          :first="(page - 1) * limit"
          :pt="pt"
          :pageLinkSize="isMobile ? 3 : 5"
          @page="({ page: newPage }) => (page = newPage + 1)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.no-wrap {
  white-space: nowrap;
}

:deep(input) {
  min-width: 350px;
}

.header-icon {
  font-size: 95%;
}

th:hover .header-icon {
  visibility: visible;
}
table {
  width: 100%;
  border-collapse: collapse;
}
</style>
