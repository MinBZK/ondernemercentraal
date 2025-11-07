<script setup lang="ts" generic="T extends Record<string, unknown>">
import InputText from 'primevue/inputtext'
import IftaLabel from 'primevue/iftalabel'
import Select from 'primevue/select'
import { formatUtcDate } from '@/util/format'
import Textarea from 'primevue/textarea'

const { t } = useI18n()

const props = defineProps<{
  field: FormField<T>
  currentValue?: FormValue
}>()

const validatorNames = computed(() => props.field.validators)

const isRequired = computed(() => !props.field.optional)

// validators
const isRequiredValidator = (value: FormValue) => {
  if (!value) return t('validation.required')
}

const validKvk = (value: FormValue) => {
  const requiredLength = 8
  const stringValue = value?.toString() || ''

  if (stringValue.length !== requiredLength) {
    return t('validation.kvkLength', { length: requiredLength })
  }
}

const containsOnlyNumericChars = (value: FormValue) => {
  const stringValue = value?.toString() || ''

  if (value && !/^\d+$/.test(stringValue)) {
    return t('validation.onlyNumbers')
  }
}

const containsNoNumericChars = (value: FormValue) => {
  const stringValue = value?.toString() || ''

  if (value && /\d/.test(stringValue)) {
    return t('validation.noNumbers')
  }
}

type ValidatorFunction = (value: FormValue) => string | undefined

const validators: Record<ValidatorNames, ValidatorFunction> = {
  required: isRequiredValidator,
  'only-numeric': containsOnlyNumericChars,
  'not-numeric': containsNoNumericChars,
  'valid-kvk': validKvk,
}

const valueInput = ref<string>()
const valueDropdown = ref<string | string[] | SelectItem>()
const valueCheckbox = ref<boolean>()
const valueDateTime = ref<Date>()
const currentValue = toRef(props, 'currentValue')

const optionsShouldBeSorted = computed(() => {
  const shouldNotBeSorted = props.field.autoSortOptions == false
  return !shouldNotBeSorted
})

const sortedOptions = computed(() => (props.field.options || []).slice().sort())

const selectOptions = computed(() =>
  optionsShouldBeSorted.value ? sortedOptions.value : props.field.options,
)

const selectHasNestedStructure = computed(() => {
  const firstOption = selectOptions.value ? selectOptions.value[0] : undefined
  return typeof firstOption == 'object' && Array.isArray((firstOption as NestedSelectItems).items)
})

function convertValueToNestedStructure(value: string | undefined): SelectItem {
  return {
    label: value || '',
    value: value,
  }
}

function parseNestedSelectValue(value: SelectItem) {
  return value.value
}

watch(
  currentValue,
  () => {
    const currentValueString = currentValue.value?.toString()
    valueInput.value = currentValueString

    if (props.field.type == 'multiselect') {
      valueDropdown.value = Array.isArray(currentValue.value) ? currentValue.value : []
    } else {
      valueDropdown.value = selectHasNestedStructure.value
        ? convertValueToNestedStructure(currentValueString)
        : currentValueString
    }

    valueCheckbox.value = Boolean(currentValue.value)

    if (currentValueString) {
      valueDateTime.value = new Date(currentValueString)
    }
  },
  {
    immediate: true,
  },
)

const applicableValue = computed(() => {
  const field = props.field
  if (field.type == 'text' || field.type == 'textarea') {
    return valueInput.value
  } else if (field.type == 'select') {
    return valueDropdown.value
  } else if (field.type == 'checkbox') {
    return valueCheckbox.value
  } else if (field.type == 'datetime') {
    return valueDateTime.value
  } else if (field.type == 'multiselect') {
    return valueDropdown.value
  } else if (field.type == 'date') {
    return valueDateTime.value
  } else {
    throw new Error(`Unknown field type: ${field.type}`)
  }
})

function filterNulls<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item != null)
}

const errors = computed(() => {
  const composedValidatorNames: ValidatorNames[] = props.field.optional
    ? validatorNames.value || []
    : ['required', ...(validatorNames.value || [])]

  const validationErrors = composedValidatorNames.map((vN) => validators[vN](applicableValue.value))
  return filterNulls(validationErrors)
})

const touched = ref<boolean>(false)

const hasDisplayedErrors = computed(() => errors.value.length > 0 && touched.value)

const emit = defineEmits<{
  updateState: [v: FormFieldState]
}>()

const state = computed((): FormFieldState => {
  return {
    value: applicableValue.value,
    errors: errors.value,
    touched: touched.value,
    valid: errors.value.length === 0,
  }
})

watch(
  state,
  (newState, oldState) => {
    if (JSON.stringify(newState) !== JSON.stringify(oldState)) {
      if (selectHasNestedStructure.value) {
        if (typeof newState.value == 'object') {
          const newStateValue = newState.value as NestedSelectItems
          newState.value = parseNestedSelectValue(newStateValue)
        }
      }
      emit('updateState', newState)
    }
  },
  {
    immediate: true,
  },
)

const placeholder = computed(() => {
  if (props.field.type == 'datetime') {
    return formatUtcDate(props.field.label(), 'longDate')
  } else {
    return props.field.label()
  }
})

const showSelectFilter = computed(() => (selectOptions.value || []).length > 5)
</script>

<template>
  <div class="w-[450px]">
    <IftaLabel v-if="field.type !== 'checkbox'" :invalid="hasDisplayedErrors">
      <InputText
        v-if="field.type == 'text'"
        v-model="valueInput"
        class="w-full"
        :input-id="field.key"
        :name="field.label()"
        type="text"
        :invalid="hasDisplayedErrors"
        :placeholder="placeholder"
        @blur="touched = true"
        :disabled="field.readOnly"
      />

      <Textarea
        v-if="field.type == 'textarea'"
        v-model="valueInput"
        class="w-full"
        :input-id="field.key"
        :name="field.label()"
        type="text"
        :invalid="hasDisplayedErrors"
        :placeholder="placeholder"
        @blur="touched = true"
        :disabled="field.readOnly"
        :rows="5"
      />

      <DatePicker
        v-else-if="field.type == 'datetime' || field.type == 'date'"
        id="datepicker-24h"
        v-model="valueDateTime"
        :show-time="field.type == 'datetime'"
        hourFormat="24"
        :disabled="field.readOnly"
        class="w-full"
        :placeholder="field.label()"
      />

      <Select
        v-else-if="field.type == 'select'"
        v-model="valueDropdown"
        class="w-full"
        :options="selectOptions"
        :placeholder="field.label()"
        :show-clear="!isRequired"
        :name="field.label()"
        :input-id="field.key.toString()"
        @blur="touched = true"
        :disabled="field.readOnly"
        :filter="showSelectFilter"
        :option-label="selectHasNestedStructure ? 'label' : undefined"
        :optionGroupLabel="selectHasNestedStructure ? 'label' : undefined"
        :optionGroupChildren="selectHasNestedStructure ? 'items' : undefined"
      >
        <template #optiongroup="slotProps">
          {{ slotProps.option['label'] }}
          <Divider />
        </template>
      </Select>

      <MultiSelect
        v-else-if="field.type == 'multiselect'"
        v-model="valueDropdown"
        class="w-full"
        :options="selectOptions"
        :placeholder="field.label()"
        :show-clear="!isRequired"
        :name="field.label()"
        :input-id="field.key.toString()"
        @blur="touched = true"
        :disabled="field.readOnly"
        :max-selected-labels="1"
        :filter="showSelectFilter"
        :option-label="selectHasNestedStructure ? 'label' : undefined"
        :optionGroupLabel="selectHasNestedStructure ? 'label' : undefined"
        :optionGroupChildren="selectHasNestedStructure ? 'items' : undefined"
      />

      <label :for="field.key.toString()">{{ field.label() }}</label>
    </IftaLabel>

    <template v-if="field.type == 'checkbox'">
      <div class="flex items-center gap-2">
        <Checkbox
          v-model="valueCheckbox"
          binary
          :input-id="field.key.toString()"
          :name="field.label()"
          :disabled="field.readOnly"
        />
        <label :for="field.label()"> {{ field.label() }} </label>
      </div>
    </template>

    <Message v-if="hasDisplayedErrors" severity="error" size="small" variant="simple">
      <span v-if="field.invalidValuePrefix">{{ field.invalidValuePrefix() }}</span>

      {{ errors.join(',') }}
    </Message>
  </div>
</template>

<style scoped>
.p-divider {
  margin: 0.5em 0 !important;
}
</style>
