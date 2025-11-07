<script setup lang="ts">
import type { components } from '@/api/schema'
import { PrimeIcons } from '@primevue/core/api'

const props = defineProps<{
  caseId?: string
  trackId?: string
}>()

const trackId = toRef(props, 'trackId')
const caseId = toRef(props, 'caseId')
const { create, updateTrack, deleteTrack, track, fetch: fetchTrack } = useTrack(trackId, caseId)
const { products, fetch: fetchProducts } = useProduct()
const { trackValues, fetch } = useTrackValue()
const { me } = useAuth()
const { trackLabels } = useEntityLabels()
fetch()
if (props.trackId) fetchTrack()
if (products.value.length === 0) fetchProducts()

const emit = defineEmits<{
  updateTrack: []
}>()

type TrackBase = components['schemas']['TrackBase']

const productCategoryOptions = computed(() =>
  [...new Set(products.value.map((p) => p.product_category_name))].sort(),
)

const productOptions = computed(() => {
  const selectedPartnerOrganization = trackValues.value?.partner_organization.find(
    (p) => p.name === trackState.partner_organization_name,
  )
  const productNames = selectedPartnerOrganization?.product_names || []

  if (selectedTrackType.value == 'Ondernemersdienstverlening') {
    return products.value
      .filter(
        (p) =>
          p.product_category_name == selectedProductCategory.value && productNames.includes(p.name),
      )
      .map((p) => p.name)
  } else {
    return productNames
  }
})

const trackConfig = computed((): FormField<TrackBase>[] => {
  return [
    {
      key: 'track_type_name',
      label: () => trackLabels.track_type_name(),
      type: 'select',
      optional: false,
      readOnly: !formCanBeEditted.value,
      options: trackValues.value?.track_type || [],
    },
    {
      key: 'product_category_name',
      label: () => trackLabels.product_category_name(),
      type: 'select',
      options: productCategoryOptions.value,
      optional: false,
      hide: selectedTrackType.value !== 'Ondernemersdienstverlening',
      readOnly: !me.value?.permissions.includes('track:update:product-category'),
    },
    {
      key: 'partner_organization_name',
      label: () => trackLabels.partner_organization_name(),
      type: 'select',
      optional: true,
      options: trackPartnerOptions.value,
      readOnly: !me.value?.permissions.includes('track:update:partner'),
    },
    {
      key: 'product_name',
      label: () => trackLabels.product_name(),
      type: 'select',
      options: productOptions.value,
      optional: true,
      hide: selectedTrackType.value !== 'Ondernemersdienstverlening',
      readOnly: !me.value?.permissions.includes('track:update:product'),
    },

    {
      key: 'priority',
      label: () => trackLabels.priority(),
      type: 'select',
      optional: false,
      options: priorityOptions,
      hide: selectedTrackType.value !== 'SHVO',
    },
    {
      key: 'status',
      label: () => trackLabels.status(),
      type: 'select',
      optional: true,
      options: trackValues.value?.status || [],
      readOnly: !stateUpdateAllowed.value,
      hide: !track.value,
    },
    {
      key: 'completion_cause',
      label: () => trackLabels.completion_cause(),
      type: 'select',
      optional: true,
      options: trackValues.value?.completion_causes || [],
      hide: track.value?.status != 'Gestart' && track.value?.status != 'Beëindigd',
      readOnly: !stateUpdateAllowed.value,
    },
    {
      key: 'completion_approved',
      label: () => trackLabels.completion_approved(),
      type: 'checkbox',
      optional: false,
      hide: !track.value,
    },
    {
      key: 'start_dt',
      label: () => trackLabels.start_dt(),
      type: 'datetime',
      optional: true,
      readOnly: true,
      hide: !track.value,
    },
    {
      key: 'end_dt',
      label: () => trackLabels.end_dt(),
      type: 'datetime',
      optional: true,
      readOnly: true,
      hide: !track.value,
    },
  ]
})

function validateNotNull(v: FormFieldState['value']) {
  if (!v) {
    throw new Error('Value is required')
  }
  return v
}

async function handleSubmit() {
  const partnerOrganization = trackState.partner_organization_name
  const trackType = validateNotNull(
    trackState.track_type_name,
  ) as components['schemas']['TrackCreate']['track_type_name']
  const trackStatus = trackState.status as components['schemas']['TrackCreate']['status']
  const completionCause = trackState.completion_cause
  const completionAprroved = Boolean(trackState.completion_approved)
  const priority = trackState.priority as components['schemas']['TrackCreate']['priority']

  if (track.value) {
    await updateTrack(
      {
        partner_organization_name: partnerOrganization,
        track_type_name: trackType,
        status: trackStatus,
        completion_cause: completionCause || null,
        completion_approved: completionAprroved,
        product_name: trackState.product_name,
        product_category_name: selectedProductCategory.value,
        priority,
      },
      track.value.id,
      track.value.case_id,
    )
  } else {
    const caseId = props.caseId
    if (!caseId) throw new Error('Case id is required for creating a track')
    await create(
      {
        partner_organization_name: partnerOrganization,
        track_type_name: trackType,
        priority,
        completion_cause: completionCause || null,
        completion_approved: completionAprroved,
        product_name: trackState.product_name,
        product_category_name: selectedProductCategory.value,
      },
      caseId,
    )
  }
  emit('updateTrack')
}

const formCanBeEditted = computed(
  () => !track.value?.completion_approved && me.value?.permissions.includes('track:update'),
)

const stateUpdateAllowed = computed(() => {
  return !track.value?.completion_approved && me.value?.permissions.includes('track:update:status')
})

const { askToConfirm } = useConfirm()
async function handleDeleteTrack(track: components['schemas']['TrackBase']) {
  await askToConfirm({
    title: 'Verwijder traject',
    question: `Weet je zeker dat je het traject wilt verwijderen?`,
  })
  await deleteTrack(track)
  emit('updateTrack')
}

type TrackPriority = Exclude<components['schemas']['Track']['priority'], undefined | null>
type TrackType = components['schemas']['Track']['track_type_name']

const priorityOptions: TrackPriority[] = ['Crisis', 'Regulier']

const selectedTrackType = computed(() => {
  const trackType = trackState['track_type_name']
  if (trackType) {
    return trackType as TrackType
  }
})

const selectedProductCategory = computed(() => {
  return trackState['product_category_name']
})

const requiredProduct = computed(() => {
  if (selectedTrackType.value == 'SHVO') {
    const requiredTrackTypeProduct: components['schemas']['AppConfig']['required_products'][0] =
      'SHVO intake'
    return requiredTrackTypeProduct
  }
})

const trackPartnerOptions = computed(
  () =>
    trackValues.value?.partner_organization
      .filter((p) => {
        const availablePartnerProductCategories = p.product_category_names
        const isAllowedByProductCategory =
          selectedProductCategory.value &&
          availablePartnerProductCategories.includes(selectedProductCategory.value)

        const isAllowedByType =
          requiredProduct.value && p.product_names.includes(requiredProduct.value)
        return isAllowedByProductCategory || isAllowedByType
      })
      .map((p) => p.name) || [],
)

const trackState: Record<keyof components['schemas']['TrackCreate'], null | string> = reactive({
  partner_organization_name: null,
  track_type_name: null,
  completion_cause: null,
  status: null,
  priority: null,
  completion_approved: null,
  product_name: null,
  product_category_name: null,
})
const formIsValid = ref(false)

const formFields = useTemplateRef('formFieldList')

watch(trackPartnerOptions, () => {
  const selectedPartnerOrgName = trackState.partner_organization_name
  const selectedPartnerOrgAllowed = selectedPartnerOrgName
    ? trackPartnerOptions.value.includes(selectedPartnerOrgName)
    : false
  if (!selectedPartnerOrgAllowed) {
    formFields.value?.mutateState({
      key: 'partner_organization_name',
      value: undefined,
    })
  }
})
</script>

<template>
  <template v-if="trackValues">
    <FormFieldList
      ref="formFieldList"
      :form-field-config="trackConfig"
      :data="track"
      @update-state="
        ({ formStateValues, isValid }) => {
          Object.assign(trackState, formStateValues)
          formIsValid = isValid
        }
      "
      :n-columns="1"
    >
      <template #after="{ field }">
        <div
          v-if="
            field.key == 'partner_organization_name' && !track?.partner_organization_name && trackId
          "
        >
          <TrackCrudRequestPartnerOrganizationChoice :track-id="trackId" />
        </div>
      </template>
    </FormFieldList>
  </template>

  <Button
    :icon="PrimeIcons.CHECK_SQUARE"
    label="Opslaan"
    class="mt-4"
    @click="handleSubmit"
    :disabled="!formIsValid"
    v-if="trackValues"
  />
  <template v-if="track && me?.permissions.includes('track:delete')">
    <Divider />

    <Button
      label="Verwijder traject"
      class="mt-2"
      :severity="'danger'"
      @click="handleDeleteTrack(track)"
    />
  </template>
</template>
