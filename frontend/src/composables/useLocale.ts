import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { computed, onMounted } from 'vue'
import { availableLocales, localeInfo, type LocaleInfo } from '@/i18n/available-locales'
import type { MessageSchema } from '@/i18n'

export function useLocale() {
  const { t } = useI18n<{ message: MessageSchema }>({
    useScope: 'global',
  })

  const router = useRouter()
  const route = useRoute()
  const { locale } = useI18n({ useScope: 'global' })

  // Get current locale information
  const currentLocaleInfo = computed<LocaleInfo>(() => localeInfo[locale.value] || localeInfo.nl)

  // Set document direction and language based on current locale
  const setDocumentAttributes = (localeCode: string) => {
    document.documentElement.setAttribute('dir', localeInfo[localeCode].dir || 'ltr')
    document.documentElement.setAttribute('lang', localeCode)
  }

  // Initialize direction and language on component mount
  // This ensures correct RTL/LTR on page refresh
  onMounted(() => {
    setDocumentAttributes(locale.value)
  })

  // Function to change locale
  const changeLocale = (newLocale: string) => {
    // Check if locale is supported
    if (!availableLocales.includes(newLocale)) {
      console.error(`Locale ${newLocale} is not supported`)
      return
    }
    locale.value = newLocale

    // Update document attributes for RTL/LTR support
    setDocumentAttributes(newLocale)

    const currentPath = route.fullPath

    let newPath = currentPath
    const localeRegex = new RegExp(`^/(${availableLocales.join('|')})`)
    const localeMatch = currentPath.match(localeRegex)

    if (localeMatch) {
      newPath = currentPath.replace(localeRegex, `/${newLocale}`)
    } else {
      newPath = `/${newLocale}${currentPath.startsWith('/') ? currentPath : '/' + currentPath}`
    }

    // Only navigate if the path actually changed
    if (newPath !== currentPath) {
      router.push(newPath)
    }
  }

  const getLocalizedPath = (path: string) => {
    // Extract the path without locale prefix
    let cleanPath = path
    if (path.match(/^\/[a-z]{2}\//)) {
      cleanPath = path.substring(3)
    } else if (path.match(/^\/[a-z]{2}$/)) {
      cleanPath = '/'
    }

    if (cleanPath === '/') {
      return `/${locale.value}`
    }

    return `/${locale.value}${cleanPath.startsWith('/') ? cleanPath : '/' + cleanPath}`
  }

  // For named routes (safer approach)
  const localizedRoute = (name: string, params = {}) => {
    return {
      name: name,
      params: {
        ...params,
        locale: locale.value,
      },
    }
  }

  return {
    locale,
    availableLocales,
    localeInfo,
    currentLocaleInfo,
    changeLocale,
    getLocalizedPath,
    localizedRoute,
    t,
  }
}
