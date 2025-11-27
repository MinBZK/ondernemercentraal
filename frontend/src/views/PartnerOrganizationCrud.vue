<script setup lang="ts">
import type { components } from '@/api/schema'
import { schemas } from '@/zod'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  partnerOrganizationId?: string
}>()

const partnerOrganizationId = toRef(props, 'partnerOrganizationId')
const { partnerOrganizationLabels } = useEntityLabels()
const {
  createPartnerOrganization,
  updatePartnerOrganization,
  fetch: fetchPartnerOrganizations,
  partnerOrganizations,
} = usePartnerOrganization(partnerOrganizationId)
fetchPartnerOrganizations()
const { products, fetch: fetchProducts } = useProduct()
fetchProducts()

const partnerOrganization = computed(() =>
  partnerOrganizations.value.find((pC) => pC.id === partnerOrganizationId.value),
)

const partnerOrganizationState = reactive({})

const partnerOrganizationConfig = computed(
  (): FormField<components['schemas']['PartnerOrganizationUpsert']>[] => {
    return [
      {
        key: 'name',
        label: () => partnerOrganizationLabels.name(),
        type: 'text',
        optional: false,
        readOnly: false,
      },
      {
        key: 'description_short',
        label: () => partnerOrganizationLabels.description_short(),
        type: 'textarea',
        optional: true,
        readOnly: false,
      },
      {
        key: 'description',
        label: () => partnerOrganizationLabels.description(),
        type: 'textarea',
        optional: true,
        readOnly: false,
      },
      {
        key: 'product_names',
        label: () => partnerOrganizationLabels.product_names(),
        type: 'multiselect',
        optional: true,
        options: products.value.map((p) => p.name).sort(),
      },
    ]
  },
)

const emit = defineEmits<{
  update: []
}>()

async function handleUpdate() {
  const partnerOrganizationCreate = schemas.PartnerOrganizationUpsert.strict()
  const parsedPayload = partnerOrganizationCreate.parse(partnerOrganizationState)
  if (!partnerOrganizationId.value) {
    await createPartnerOrganization(parsedPayload)
  } else {
    await updatePartnerOrganization(parsedPayload)
  }
  emit('update')
}

const { me } = useAuth()
const formIsValid = ref(false)
</script>

<template>
  <FormFieldList
    :form-field-config="partnerOrganizationConfig"
    :data="partnerOrganization"
    @update-state="
      ({ formStateValues, isValid }) => {
        Object.assign(partnerOrganizationState, formStateValues)
        formIsValid = isValid
      }
    "
    :n-columns="1"
  />
  <Button
    class="mt-4"
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    @click="handleUpdate()"
    :disabled="!formIsValid"
    v-if="me?.permissions.includes('partner-organization:create')"
  />
</template>
