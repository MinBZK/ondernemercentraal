<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'
import { sortArrayByKey } from '@/util'

const {
  productCategories,
  fetch: fetchProductCategories,
  deleteProductCategory,
} = useProductCategory()
const { productCategoryLabels } = useEntityLabels()
fetchProductCategories()

const { me } = useAuth()
const showCrud = ref(false)

type ProductCategory = components['schemas']['ProductCategory']

const productCategoryConfig: TableColumnConfig<ProductCategory>[] = [
  {
    key: 'name',
    label: productCategoryLabels.name,
  },
  {
    key: 'created_at',
    label: productCategoryLabels.created_at,
    dataType: 'datetime',
  },
]

const selectedProductCategory = ref<ProductCategory>()

type ContextMenuActions = 'Bewerken' | 'Verwijderen'

const menuItems: ContextMenuItem<ContextMenuActions>[] = [
  {
    icon: PrimeIcons.FILE_EDIT,
    label: 'Bewerken',
    hide: !me.value?.permissions.includes('product-category:update'),
  },
  {
    icon: PrimeIcons.TRASH,
    label: 'Verwijderen',
    hide: !me.value?.permissions.includes('product-category:delete'),
  },
]

async function handleDelete(productCategory: ProductCategory) {
  await deleteProductCategory(productCategory.id)
  fetchProductCategories()
}
</script>

<template>
  <Dialog
    v-model:visible="showCrud"
    header="Pijler"
    :modal="true"
    :dismissable-mask="true"
    @update="selectedProductCategory = undefined"
  >
    <ProductCategoryCrud
      :product-category-id="selectedProductCategory?.id"
      @update="[
        (showCrud = false),
        (selectedProductCategory = undefined),
        fetchProductCategories(),
      ]"
    />
  </Dialog>
  <Button
    v-if="me?.permissions.includes('product-category:create')"
    @click="showCrud = true"
    size="small"
    :variant="'outlined'"
    :icon="PrimeIcons.PLUS"
    label="Pijler"
  />
  <OcTable
    :data="sortArrayByKey(productCategories, 'updated_at').reverse()"
    :table-config="productCategoryConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #action="{ row: currentPc }">
      <ContextMenu
        :menu-items="menuItems"
        @item-clicked="
          (item) => {
            if (item.label === 'Verwijderen') {
              handleDelete(currentPc)
            } else if (item.label === 'Bewerken') {
              selectedProductCategory = currentPc
              showCrud = true
            }
          }
        "
      />
    </template>
  </OcTable>
</template>
