<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  productCategoryId?: string
}>()

const productCategoryId = toRef(props, 'productCategoryId')
const { productCategoryLabels } = useEntityLabels()
const {
  createProductCategory,
  updateProductCategory,
  fetch: fetchProductCategories,
  productCategories,
} = useProductCategory()
fetchProductCategories()

const productCategory = computed(() =>
  productCategories.value.find((pC) => pC.id === productCategoryId.value),
)

const productCategoryState = reactive({})

const productCategoryConfig = computed(
  (): FormField<components['schemas']['ProductCategoryCreate']>[] => {
    return [
      {
        key: 'name',
        label: () => productCategoryLabels.name(),
        type: 'text',
        optional: false,
        readOnly: false,
      },
    ]
  },
)

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const productCreate = schemas.ProductCategoryCreate.strict()
  const parsedPayload = productCreate.parse(productCategoryState)
  if (!productCategoryId.value) {
    await createProductCategory(parsedPayload.name)
  } else {
    await updateProductCategory(productCategoryId.value, parsedPayload.name)
  }
  emit('update')
}

const { me } = useAuth()
const formIsValid = ref(false)
</script>

<template>
  <FormFieldList
    :form-field-config="productCategoryConfig"
    :data="productCategory"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(productCategoryState, formStateValues)
        formIsValid = isValid
      }
    "
  />
  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    :disabled="!formIsValid"
    v-if="me?.permissions.includes('product-category:create')"
  />
</template>
