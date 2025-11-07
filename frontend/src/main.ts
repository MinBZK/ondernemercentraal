import PrimeVue from 'primevue/config'
import { createApp } from 'vue'
import App from './App.vue'
import RoPreset from '@/config/primevue-theme-rijksoverheid'
import i18n from './i18n'
import localeConfig from '@/config/locale'
import ToastService from 'primevue/toastservice'
import router from '@/router'
import { createHead } from '@unhead/vue/client'
import Ripple from 'primevue/ripple'

import 'primeicons/primeicons.css'
import './assets/styles/main.css'

const app = createApp(App)
const head = createHead()
const { fetch: fetchConfig, config } = useConfig()

const locale = localeConfig['nl']

async function initApp() {
  await fetchConfig()
  if (config.value?.tenant_config.primary_color) {
    document.documentElement.style.setProperty(
      '--color-primary',
      config.value?.tenant_config.primary_color,
    )
  }

  return
}

initApp().then(() => {
  app.use(ToastService)
  app.use(head)
  app.use(router)
  app.use(i18n)
  app.use(PrimeVue, {
    csp: {
      nonce: 'IctuDevopsi18s',
    },
    ripple: true,
    locale,
    theme: {
      preset: RoPreset,
      options: {
        darkModeSelector: false || 'none',
      },
    },
  })
  app.directive('ripple', Ripple)
  app.mount('#app')
})
