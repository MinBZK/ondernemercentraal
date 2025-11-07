<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'
const { t } = useLocale()

const { availableLocales, localeInfo, changeLocale, locale } = useLocale()
const { userAuthenticated } = useAuth()

const languageOptions = computed(() => {
  return availableLocales.map((lang) => ({
    label: localeInfo[lang].name,
    value: lang,
  }))
})

const selectedLanguage = computed({
  get: () => locale.value,
  set: (newValue) => {
    changeLocale(newValue)
    showLanguageDropdown.value = false
  },
})

const showLanguageDropdown = ref(false)
</script>

<template>
  <div v-if="!userAuthenticated" class="md:inline-flex items-center ml-4 hidden">
    <Select
      v-model="selectedLanguage"
      :options="languageOptions"
      option-label="label"
      option-value="value"
      :placeholder="localeInfo[locale].name"
      :aria-label="t('common.appTitle')"
    />
  </div>

  <div v-if="!userAuthenticated" class="flex items-center text-white relative md:hidden">
    <i :class="[PrimeIcons.GLOBE, 'px-2']" />
    <Select
      v-model="selectedLanguage"
      :options="languageOptions"
      option-label="label"
      option-value="value"
      :placeholder="localeInfo[locale].name"
      :aria-label="t('common.thisWebsiteInOtherLanguages')"
      class="w-auto min-w-[120px]"
    />
  </div>
</template>
