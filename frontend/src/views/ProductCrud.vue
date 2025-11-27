<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  productId?: string
}>()

const productId = toRef(props, 'productId')
const { productLabels } = useEntityLabels()
const { createProduct, updateProduct, fetch: fetchProducts, products } = useProduct()
const { productCategories, fetch: fetchProductCategories } = useProductCategory()
fetchProductCategories()
fetchProducts()

const product = computed(() => products.value.find((p) => p.id === productId.value))

const productConfig = computed((): FormField<components['schemas']['ProductCreate']>[] => {
  return [
    {
      key: 'name',
      label: () => productLabels.name(),
      type: 'text',
      optional: false,
      readOnly: false,
    },
    {
      key: 'code',
      label: () => productLabels.code(),
      type: 'text',
      optional: true,
    },
    {
      key: 'product_category_name',
      label: () => productLabels.product_category_name(),
      type: 'select',
      options: productCategories.value.map((pC) => pC.name).sort(),
      optional: false,
    },
  ]
})

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const productCreate = schemas.ProductCreate.strict()
  const parsedPayload = productCreate.parse(productState)
  if (!productId.value) {
    await createProduct(parsedPayload)
  } else {
    await updateProduct(parsedPayload, productId.value)
  }
  emit('update')
}

const { me } = useAuth()
const formIsValid = ref(false)
const productState: Record<keyof components['schemas']['ProductCreate'], unknown> = reactive({
  name: undefined,
  code: undefined,
  product_category_name: undefined,
})
</script>

<template>
  <FormFieldList
    :form-field-config="productConfig"
    :data="product"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(productState, formStateValues)
        formIsValid = isValid
      }
    "
    :n-columns="1"
  />
  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    :disabled="!formIsValid"
    v-if="me?.permissions.includes('product:create')"
  />
</template>
