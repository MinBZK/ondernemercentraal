<script setup lang="ts">
const route = useRoute()
const { changeLocale } = useLocale()

watchEffect(() => {
  if (route.params.locale) {
    changeLocale(route.params.locale.toString())
  }
})
</script>

<template>
  <router-view />
</template>
