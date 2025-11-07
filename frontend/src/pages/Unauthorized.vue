<script lang="ts" setup>
const { keycloak } = useKeycloak()

const { baseUrl } = useConfig()
</script>

<template>
  <Page page-title="Geen toegang">
    <p>
      Je hebt geen rechten om deze pagina te bekijken. Neem contact op met devops@ictu.nl als je
      denkt dat dit een fout is.
    </p>
    <Button
      @click="
        keycloak?.logout({
          redirectUri: baseUrl,
        })
      "
      >Uitloggen</Button
    >
  </Page>
</template>
