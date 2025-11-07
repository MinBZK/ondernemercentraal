import router from '@/router'

import Keycloak from 'keycloak-js'

const keycloak = ref<Keycloak>()

const { token: authToken } = useAuth()
const { registerAuthMiddleware } = useApiClient()
const { config } = useConfig()

export const handleLogin = async (targetUrl: string) => {
  if (!keycloak.value) {
    throw new Error('Keycloak client not initialized')
  }
  const redirectUri = window.location.origin + targetUrl
  await keycloak.value.login({ redirectUri })
}

// Initialize Keycloak only once
async function initKeycloakClient() {
  keycloak.value = new Keycloak({
    url: config.value.keycloak_uri,
    realm: config.value.keycloak_realm,
    clientId: config.value.keycloak_client_id,
  })
  const authorized = await keycloak.value.init({
    onLoad: 'login-required',
  })
  if (authorized) {
    registerMiddlewareAndToken(keycloak.value)
    return keycloak.value
  } else {
    handleLogin('/beheer')
  }
}

function registerMiddlewareAndToken(keycloakClient: Keycloak) {
  const token = keycloakClient.token
  if (!token) {
    handleLogin('/')
  } else {
    registerAuthMiddleware(() => token)

    // Token refresh logic
    setInterval(async () => {
      try {
        const refreshed = await keycloakClient.updateToken(70) // Refresh only if expiring in 5s
        if (refreshed) {
          authToken.value = keycloakClient.token || ''
          registerAuthMiddleware(() => authToken.value)
        }
      } catch (error) {
        console.warn('Token refresh failed, forcing re-login:', error)
        router.push({ name: 'Login' })
      }
    }, 5000) // Run every 5 seconds to check token expiry
  }
}

async function getKeycloakClient() {
  const keycloakClient = keycloak.value || (await initKeycloakClient())
  return keycloakClient
}

export function useKeycloak() {
  return { keycloak, getKeycloakClient, handleLogin }
}
