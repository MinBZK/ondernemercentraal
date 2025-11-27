import type { components } from '@/api/schema'

const { client: apiClient } = useApiClient()

const products = ref<components['schemas']['Product'][]>([])

async function fetch() {
  const { data } = await apiClient.GET('/api/product/')
  if (!data) throw new Error('No products returned')
  products.value = data
}

function createProduct(productNew: components['schemas']['ProductCreate']) {
  return apiClient.POST('/api/product/', {
    body: productNew,
  })
}

function updateProduct(productUpdate: components['schemas']['ProductUpdate'], prodictId: string) {
  return apiClient.PUT('/api/product/{product_id}', {
    body: productUpdate,
    params: {
      path: {
        product_id: prodictId,
      },
    },
  })
}

function deleteProduct(product: components['schemas']['Product']) {
  return apiClient.DELETE('/api/product/{product_id}', {
    params: {
      path: {
        product_id: product.id,
      },
    },
  })
}

export function useProduct() {
  return {
    fetch,
    createProduct,
    updateProduct,
    deleteProduct,
    products,
  }
}
