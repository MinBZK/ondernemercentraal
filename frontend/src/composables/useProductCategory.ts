import type { components } from '@/api/schema'

const { client: apiClient } = useApiClient()

const productCategories = ref<components['schemas']['ProductCategory'][]>([])

async function fetch() {
  const { data } = await apiClient.GET('/api/product-category/')
  if (!data) throw new Error('No product categories returned')
  productCategories.value = data
}

function createProductCategory(name: string) {
  return apiClient.POST('/api/product-category/', {
    body: {
      name: name,
    },
  })
}

function updateProductCategory(id: string, name: string) {
  return apiClient.PUT('/api/product-category/{product_category_id}', {
    body: {
      name: name,
    },
    params: {
      path: {
        product_category_id: id,
      },
    },
  })
}

function deleteProductCategory(id: string) {
  return apiClient.DELETE('/api/product-category/{product_category_id}', {
    params: {
      path: {
        product_category_id: id,
      },
    },
  })
}

export function useProductCategory() {
  return {
    productCategories,
    fetch,
    createProductCategory,
    updateProductCategory,
    deleteProductCategory,
  }
}
