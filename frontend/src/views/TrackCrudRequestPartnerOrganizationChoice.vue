<script setup lang="ts">
import { PrimeIcons } from '@primevue/core/api'
import type { MenuItem } from 'primevue/menuitem'
import type { RouteLocationRaw } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const props = defineProps<{
  trackId: string
}>()

const label = 'Verzoek ondernemer om een partnerorganisatie te kiezen'

const trackId = toRef(props, 'trackId')
const caseId = ref()
const { requestPartnerOrganizationChoice } = useTrack(trackId, caseId)

const targetRoute: RouteLocationRaw = {
  name: 'BeheerTrackPartnerOrganization',
  params: { trackId: props.trackId },
}

const router = useRouter()
const toast = useToast()

const items: MenuItem[] = [
  {
    label: 'Kopieër link',
    icon: PrimeIcons.COPY,
    command: () => {
      const { fullPath } = router.resolve(targetRoute)
      navigator.clipboard.writeText(`${window.origin}${fullPath}`)
      toast.add({
        severity: 'success',
        summary: 'Link gekopieerd',
        detail: 'De link naar de keuzepagina is gekopieerd naar het klembord.',
        life: 3000,
      })
    },
  },
  {
    label: 'Bekijk keuzepagina',
    icon: PrimeIcons.EYE,
    command: () => {
      router.push(targetRoute)
    },
  },
]

const { notify } = useNotification()
async function handleSendRequest() {
  await requestPartnerOrganizationChoice()
  notify({
    severity: 'success',
    message:
      'Er is een e-mail verstuurd naar de ondernemer met het verzoek om een partnerorganisatie te kiezen.',
  })
}
</script>

<template>
  <SplitButton
    :label="label"
    @click="handleSendRequest()"
    :model="items"
    :icon="PrimeIcons.ENVELOPE"
  />
</template>
