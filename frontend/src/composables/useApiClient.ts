import createClient, { type Middleware } from 'openapi-fetch'
import type { paths } from '@/api/schema'
const { notify } = useNotification()

const baseUrl: string =
  import.meta.env.MODE == 'production' ? window.location.origin : import.meta.env.VITE_API_URL

const client = createClient<paths>({ baseUrl })

const getFullUrl = (endpoint: keyof paths) => {
  return baseUrl + endpoint
}

const token = ref<string>()

export function useApiClient() {
  let getToken = () => ''

  function registerAuthMiddleware(tokenProvider: () => string) {
    getToken = tokenProvider

    const middleware: Middleware = {
      onRequest({ request }) {
        token.value = getToken()
        if (token.value) {
          request.headers.set('Authorization', `Bearer ${token.value}`)
        } else {
          console.error('No token available.')
        }
        return request
      },
      async onResponse({ response }) {
        if (!response.ok) {
          const error = await response.clone().text()
          notify({
            message: error,
            severity: 'error',
          })
          throw new Error(error)
        }
        return response
      },
    }

    client.use(middleware)
  }

  return { client, registerAuthMiddleware, baseUrl, getFullUrl, token }
}
