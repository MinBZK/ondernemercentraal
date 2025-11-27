/// <reference types="vite/client" />
/// <reference types="vite/client" />

export type {}

declare global {
  interface NavigatieItems {
    label: string
    hide?: boolean
    icon?: string
    routeName?: string
    routePath?: string
    highlightOnRoutes?: string[]
    requiredPermission?: GebruikerPermissions
  }

  type FormFieldValue = string | null | undefined | boolean

  type FormResolveInput = {
    value: FormFieldValue
  }

  type ValidatorNames = 'only-numeric' | 'required' | 'not-numeric' | 'valid-kvk'

  type FormField<T> = {
    key: keyof T
    label: () => string
    type:
      | 'text'
      | 'select'
      | 'checkbox'
      | 'datetime'
      | 'multiselect'
      | 'textarea'
      | 'custom'
      | 'date'
    options?: string[] | NestedSelectItems[] // voor dropdowns
    description?: string // optioneel, extra uitleg
    optional: boolean
    readOnly?: boolean
    autoSortOptions?: boolean
    invalidValuePrefix?: () => string
    hide?: boolean
    defaultValue?: FormFieldValue
    validators?: ValidatorNames[]
  }

  type FormValue = string | boolean | undefined | null | string[] | Date | Record<string, Any>

  type FormFieldState = {
    value: FormValue
    errors: string[]
    touched: boolean
    valid: boolean
  }

  type DataTypeDateLike = 'date' | 'date-long' | 'datetime' | 'relative-datetime' | 'time'

  type DataType = 'text' | 'number' | 'boolean' | 'string-list' | 'custom' | DataTypeDateLike

  type EntityAttribute = {
    label: () => string
    dataType?: DataType
    hidden?: boolean
  }

  type TableColumnConfig<T> = EntityAttribute & {
    key: keyof T
    columnWidth?: 'w-1/2' | 'w-1/3' | 'w-1/4' | 'w-1/5' | 'w-1/6'
    noWrap?: boolean
    hide?: boolean
    // this should be a key of the nested object, not a key of T
    stringifiedValueKey?: string
  }

  type EntityAttributeConfig<T> = Record<keyof T, EntityAttribute | undefined>

  type RowLinkParam<T> = {
    routeIdKey: string
    idKey: keyof T
  }

  type RowLinkConfig<T> = {
    routeName: string | ((row: T) => string)
    params: RowLinkParam<T>[]
  }

  type EntityLabels<T> = keyof T
  type EntityLabelDictionary<T> = Record<EntityLabels<T>, () => string>

  type ContextMenuItem<T> = {
    icon: string
    label: T
    hide?: boolean
  }

  // eslint-disable-next-line
  type TableValue = any

  type SelectItem = {
    label: string
    value?: string
  }

  type NestedSelectItems = SelectItem & {
    items: SelectItem[]
  }

  type FormState = Record<string, FormFieldState | undefined>
  type FormStateValues = Record<string, FormValue>
  type StatePayload = {
    formStateValues: FormStateValues
    isValid: boolean
  }

  type FormDataCreateRoutes = 'BeheerAppointmentFormCreate' | 'BeheerTrackFormCreate'
  type FormDataViewRoutes =
    | 'BeheerAppointmentFormData'
    | 'BeheerTrackFormData'
    | 'BeheerRequestFormData'
}
