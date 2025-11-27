<script setup lang="ts">
import router from '@/router'
import { PrimeIcons } from '@primevue/core/api'
const { notify } = useNotification()

const props = defineProps<{
  caseId: string
}>()

const { t } = useLocale()

const caseId = toRef(props, 'caseId')

const { clientCase, fetch, deleteCase, fetchCases } = useCase(caseId)
const clientId = computed(() => clientCase.value?.client.id)
const { createUser } = useClient(clientId)
const { askToConfirm } = useConfirm()

fetch()

const showClient = ref(false)
const clientHasUser = computed(() => Boolean(clientCase.value?.client.user))
const { me } = useAuth()

async function handleCreateUser() {
  const { message } = await createUser()
  notify({ message })
  fetchCases()
}
</script>

<template>
  <Page page-title="Dossier" v-if="clientCase">
    <strong>Dossiernummer:</strong> {{ clientCase.case_number }}
    <h2>Ondernemer</h2>
    {{ clientCase.client_initials }}
    {{ clientCase.client_last_name }} ({{ clientCase.client_company_name }})<Button
      @click="showClient = true"
      size="small"
      :variant="'outlined'"
      :icon="PrimeIcons.SEARCH"
      class="ml-2"
    />
    <div class="mt-2" v-if="me?.permissions.includes('client:create-user')">
      <Button
        size="small"
        :variant="'outlined'"
        :icon="PrimeIcons.USER_PLUS"
        label="Account aanmaken"
        @click="handleCreateUser()"
        :disabled="clientHasUser"
      />
      <div v-if="clientHasUser">De client heeft een gebruikersaccount.</div>
    </div>

    <Dialog
      v-model:visible="showClient"
      :header="t('entities.client')"
      :modal="true"
      :dismissable-mask="true"
    >
      <ClientCrud :client-id="clientCase.client.id" @update="[fetch(), (showClient = false)]" />
    </Dialog>

    <h2>Adviseur</h2>
    <div class="max-w-sm">
      <BeheerSelectAdvisor :selected-advisor="clientCase.advisor ?? undefined" :case-id="caseId" />
    </div>

    <h2>Gesprekken</h2>
    <AppointmentTable :case-id="caseId" />

    <h2 class="mt-4">Trajecten</h2>
    <TrackTable :case-id="caseId" />

    <template v-if="me?.permissions.includes('task:read')">
      <h2 class="mt-4">Taken</h2>
      <TaskTable :case-id="caseId" />
    </template>

    <template v-if="me?.permissions.includes('request:read')">
      <h2 class="mt-4">Aanvragen</h2>
      <RequestTable :case-id="caseId" />
    </template>

    <template v-if="me?.permissions.includes('case:file:read')">
      <h2 class="mt-4">Bestanden</h2>
      <FileCrudCase :case-id="caseId" :required-file-types="[]" />
    </template>

    <template v-if="me?.permissions.includes('comment:read')">
      <h2 class="mt-4">Notities</h2>
      <CommentCrud :case-id="caseId" />
    </template>

    <template v-if="clientCase">
      <Divider />
      <Button
        label="Verwijder dit dossier"
        @click="
          async () => {
            if (!clientCase) {
              throw new Error('Case is undefined')
            }
            await askToConfirm({
              question:
                'Weet je zeker dat je dit dossier wilt verwijderen? Dit kan niet ongedaan worden gemaakt.',
              title: 'Dossier verwijderen',
            })
            await deleteCase(clientCase.id)
            await fetchCases()
            router.push({ name: 'BeheerCaseMany' })
          }
        "
        :severity="'danger'"
      />
    </template>
  </Page>
</template>

<style scoped>
h2 {
  margin-top: 1em;
}
</style>
