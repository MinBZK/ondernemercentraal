<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'
import { sortArrayByKey } from '@/util'

const { products, fetch: fetchProducts, deleteProduct } = useProduct()
const { fetch: fetchProductCategories, productCategories } = useProductCategory()
const { productLabels } = useEntityLabels()
fetchProductCategories()
fetchProducts()

watch(productCategories, () => fetchProducts())

const { me } = useAuth()
const showCrud = ref(false)

type Product = components['schemas']['Product']

const productConfig: TableColumnConfig<Product>[] = [
  {
    key: 'name',
    label: productLabels.name,
  },
  {
    key: 'code',
    label: productLabels.code,
  },
  {
    key: 'product_category_name',
    label: productLabels.product_category_name,
    dataType: 'text',
  },
  {
    key: 'created_at',
    label: productLabels.created_at,
    dataType: 'datetime',
  },
]

const selectedProduct = ref<Product>()

type ContextMenuActions = 'Bewerken' | 'Verwijderen'

const menuItems: ContextMenuItem<ContextMenuActions>[] = [
  {
    icon: PrimeIcons.FILE_EDIT,
    label: 'Bewerken',
    hide: !me.value?.permissions.includes('product:update'),
  },
  {
    icon: PrimeIcons.TRASH,
    label: 'Verwijderen',
    hide: !me.value?.permissions.includes('product:delete'),
  },
]

async function handleDelete(product: Product) {
  await deleteProduct(product)
  fetchProducts()
}
</script>

<template>
  <Dialog
    v-model:visible="showCrud"
    header="Dienstverlening"
    :modal="true"
    :dismissable-mask="true"
    @update="selectedProduct = undefined"
  >
    <ProductCrud
      :product-id="selectedProduct?.id"
      @update="[(showCrud = false), (selectedProduct = undefined), fetchProducts()]"
    />
  </Dialog>
  <Button
    v-if="me?.permissions.includes('product:create')"
    @click="showCrud = true"
    size="small"
    :variant="'outlined'"
    :icon="PrimeIcons.PLUS"
    label="Dienstverlening"
  />
  <OcTable
    :data="sortArrayByKey(products, 'updated_at').reverse()"
    :table-config="productConfig"
    :id-key="'id'"
    :limit="5"
    show-action-column
  >
    <template #action="{ row: currentProduct }">
      <ContextMenu
        :menu-items="menuItems"
        @item-clicked="
          (item) => {
            if (item.label === 'Verwijderen') {
              handleDelete(currentProduct)
            } else if (item.label === 'Bewerken') {
              selectedProduct = currentProduct
              showCrud = true
            }
          }
        "
      />
    </template>
  </OcTable>
</template>
