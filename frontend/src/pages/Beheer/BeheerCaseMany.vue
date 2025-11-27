<script setup lang="ts">
import { sortArrayByKey } from '@/util'
import type { UnwrapRef } from 'vue'

const { cases, fetchCases } = useCase()
fetchCases()

type Case = UnwrapRef<typeof cases>[0]
type CaseTableConfig = TableColumnConfig<Case>

const { caseLabels } = useEntityLabels()

const caseTableConfig: CaseTableConfig[] = [
  {
    key: 'case_number',
    label: () => caseLabels.case_number(),
  },
  {
    key: 'client_bsn',
    label: () => caseLabels.client_bsn(),
  },
  {
    key: 'client_initials',
    label: () => caseLabels.client_initials(),
  },
  {
    key: 'client_last_name',
    label: () => caseLabels.client_last_name(),
  },
  {
    key: 'is_active',
    label: () => caseLabels.is_active(),
    dataType: 'boolean',
  },
  {
    key: 'advisor',
    label: () => caseLabels.advisor(),
    dataType: 'custom',
    stringifiedValueKey: 'name',
  },
  {
    key: 'created_at',
    label: () => caseLabels.created_at(),
    dataType: 'datetime',
  },
]
</script>

<template>
  <Page page-title="Dossiers">
    <OcTable
      :data="sortArrayByKey(cases, 'created_at')"
      :table-config="caseTableConfig"
      :id-key="'id'"
      :show-action-column="true"
      :row-link-config="{
        routeName: 'BeheerCaseDetail',
        params: [
          {
            routeIdKey: 'caseId',
            idKey: 'id',
          },
        ],
      }"
    >
      <template #custom="{ column, row: ocCase }">
        <template v-if="column.key === 'advisor'">
          <BeheerSelectAdvisor
            :selected-advisor="ocCase.advisor || undefined"
            :case-id="ocCase.id"
          />
        </template>
      </template>
    </OcTable>
  </Page>
</template>
