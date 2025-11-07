<script setup lang="ts">
import type { components } from '@/api/schema'
import { z } from 'zod'
import { schemas } from '@/zod'
import router from '@/router'
const { notify } = useNotification()
import { getFormValues } from '@/util'
import { joinStringsSemantic } from '@/util'

const { t } = useLocale()
const { clientLabels } = useEntityLabels()

const LocationSchema = schemas.ClientLocation.strict()
const DetailsSchema = schemas.ClientDetails.strict()

type Location = z.infer<typeof LocationSchema>
type Details = z.infer<typeof DetailsSchema>

const { config } = useConfig()

const fieldsLocation = computed((): FormField<Location>[] => {
  return [
    {
      key: 'company_location',
      label: clientLabels['company_location'],
      validators: [],
      type: 'select',
      optional: LocationSchema.shape.company_location.isOptional(),
      options: [...[...config.value.tenant_config.company_locations].sort(), 'Andere gemeente'],
      autoSortOptions: false,
    },
    {
      key: 'residence_location',
      label: clientLabels['residence_location'],
      optional: LocationSchema.shape.residence_location.isOptional(),
      type: 'select',
      options: [...[...config.value.tenant_config.residence_locations].sort(), 'Andere gemeente'],
      autoSortOptions: false,
    },
  ]
})

const fieldsDetails: FormField<Details>[] = [
  {
    key: 'initials',
    label: clientLabels['initials'],
    validators: ['not-numeric'],
    type: 'text',
    optional: DetailsSchema.shape.initials.isOptional(),
  },
  {
    key: 'last_name_prefix',
    label: clientLabels['last_name_prefix'],
    type: 'text',
    validators: ['not-numeric'],
    optional: DetailsSchema.shape.last_name_prefix.isOptional(),
  },
  {
    key: 'last_name',
    label: clientLabels['last_name'],
    validators: ['not-numeric'],
    type: 'text',
    optional: DetailsSchema.shape.last_name.isOptional(),
  },
  {
    key: 'company_name',
    label: clientLabels['company_name'],
    type: 'text',
    optional: DetailsSchema.shape.company_name.isOptional(),
  },
  {
    key: 'kvk_number',
    label: clientLabels['kvk_number'],
    validators: ['only-numeric', 'valid-kvk'],
    type: 'text',
    optional: DetailsSchema.shape.kvk_number.isOptional(),
  },
  {
    key: 'bsn',
    label: clientLabels['bsn'],
    validators: ['only-numeric'],
    type: 'text',
    optional: DetailsSchema.shape.bsn.isOptional(),
    invalidValuePrefix: () => t('pages.appointment.validationMessages.bsn'),
  },
  {
    key: 'phone_number',
    label: clientLabels['phone_number'],
    validators: ['only-numeric'],
    type: 'text',
    optional: DetailsSchema.shape.phone_number.isOptional(),
    invalidValuePrefix: () => t('pages.appointment.validationMessages.phone_number'),
  },
  {
    key: 'email',
    label: clientLabels['email'],
    type: 'text',
    optional: DetailsSchema.shape.email.isOptional(),
  },
  {
    key: 'agree_to_share_data',
    label: clientLabels['agree_to_share_data'],
    type: 'checkbox',
    optional: DetailsSchema.shape.agree_to_share_data.isOptional(),
  },
]

const { validateLocation, create: createClient } = useClient()

const formStateLocation = reactive<Record<keyof Location, FormFieldState | undefined>>({
  company_location: undefined,
  residence_location: undefined,
})

const formStateDetails = reactive<Record<keyof Details, FormFieldState | undefined>>({
  last_name: undefined,
  company_name: undefined,
  agree_to_share_data: undefined,
  kvk_number: undefined,
  phone_number: undefined,
  initials: undefined,
  last_name_prefix: undefined,
  bsn: undefined,
  email: undefined,
})

const initialValuesDefault = {
  last_name: undefined,
  company_name: undefined,
  agree_to_share_data: undefined,
  kvk_number: undefined,
  phone_number: undefined,
  initials: undefined,
  last_name_prefix: undefined,
  bsn: undefined,
  residence_location: undefined,
  company_location: undefined,
  email: undefined,
}

const initialValues =
  reactive<Record<keyof Location | keyof Details, FormValue>>(initialValuesDefault)

const formValuesLocation = computed(() => getFormValues<keyof Location>(formStateLocation))
const formValuesDetail = computed(() => getFormValues<keyof Details>(formStateDetails))

async function handleLocationValidation() {
  try {
    const location = LocationSchema.parse(formValuesLocation.value)
    locationValidation.value = await validateLocation(location)
  } catch {
    console.error('Location values invalid')
    locationValidation.value = undefined
  }
}

const locationValidation = ref<components['schemas']['ValidationResult']>()
handleLocationValidation()
watch(
  formStateLocation,
  async () => {
    handleLocationValidation()
  },
  {
    deep: true,
    immediate: true,
  },
)

const showDetails = computed(() => locationValidation.value && locationValidation.value.valid)

const formStateValid = computed(() => {
  const formFieldStates = [...Object.values(formStateLocation), ...Object.values(formStateDetails)]
  return formFieldStates.every((s) => s?.valid)
})

async function handleSubmit() {
  const location = LocationSchema.parse(formValuesLocation.value)
  const details = DetailsSchema.parse(formValuesDetail.value)
  try {
    await createClient(location, details)
    router.push({ name: 'AppointmentClientCreated', params: { locale: 'nl' } })
  } catch {
    notify({
      message: t('pages.appointment.create.signupError'),
      severity: 'error',
    })
  }
}

const allowedGemeentes = computed(() =>
  joinStringsSemantic(config.value.tenant_config.allowed_gemeentes, 'en'),
)
</script>

<template>
  <Page :page-title="t('pages.appointment.create.title')">
    <h2>{{ t('pages.appointment.create.headerIntroduction') }}</h2>
    <span> {{ t('pages.appointment.create.introduction') }}&nbsp;{{ allowedGemeentes }}.</span>
    <h2 class="text-md mt-4">{{ t('pages.appointment.create.residenceWorkHeading') }}</h2>
    <form class="flex flex-col gap-2 w-full sm:w-120" @submit.prevent="handleSubmit">
      <FormFieldCore
        v-for="f in fieldsLocation"
        :key="f.label()"
        :field="f"
        :current-value="initialValues[f.key]"
        :validator-names="f.validators"
        @update-state="
          (v) => {
            formStateLocation[f.key] = v
          }
        "
      />

      <span v-if="locationValidation !== undefined && locationValidation.valid === false">
        {{ t('pages.appointment.create.locationValidationError') }}&nbsp;{{ allowedGemeentes }}.
      </span>
      <template v-if="showDetails">
        <h2 class="text-md">{{ t('pages.appointment.create.yourDetails') }}</h2>

        <FormFieldCore
          v-for="f in fieldsDetails"
          :key="f.label()"
          :field="f"
          :validator-names="f.validators"
          :current-value="initialValues[f.key]"
          @update-state="
            (v) => {
              formStateDetails[f.key] = v
            }
          "
        />
        <Button
          type="submit"
          :label="t('pages.appointment.create.submitButton')"
          :disabled="!formStateValid"
        />
      </template>
    </form>
  </Page>
</template>

<style scoped>
h2 {
  font-size: 1em !important;
}
</style>
