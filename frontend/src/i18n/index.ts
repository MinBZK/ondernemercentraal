import { createI18n } from 'vue-i18n'
import nl from './locales/nl.json'
import en from './locales/en.json'
import ar from './locales/ar.json'
import { availableLocales } from './available-locales'

const getLocaleFromPath = () => {
  const path = window.location.pathname
  const localeFromPath = path.split('/')[1]
  return availableLocales.includes(localeFromPath) ? localeFromPath : null
}

const getBrowserLocale = () => {
  const browserLocale = navigator.language.split('-')[0]
  return availableLocales.includes(browserLocale) ? browserLocale : 'nl'
}

// Determine the locale to use (prioritize URL path)
const locale = getLocaleFromPath() ?? getBrowserLocale()

export type MessageSchema = typeof nl

const i18n = createI18n<[MessageSchema], 'nl' | 'en' | 'ar'>({
  legacy: false,
  locale: locale,
  globalInjection: true,
  fallbackLocale: 'nl',
  messages: {
    nl,
    ar,
    en,
  },
})

export default i18n
