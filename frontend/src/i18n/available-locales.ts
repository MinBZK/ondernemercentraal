export const availableLocales = ['nl', 'en', 'ar']

export interface LocaleInfo {
  code: string
  name: string
  dir?: 'ltr' | 'rtl'
}

export const localeInfo: Record<string, LocaleInfo> = {
  nl: { code: 'nl', name: 'Nederlands', dir: 'ltr' },
  en: { code: 'en', name: 'English', dir: 'ltr' },
  ar: { code: 'ar', name: 'العربية', dir: 'rtl' },
}
