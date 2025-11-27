import { makeApi, Zodios, type ZodiosOptions } from '@zodios/core'
import { z } from 'zod'

const AppointmentPublic = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    start_time: z.union([z.string(), z.null()]),
    end_time: z.union([z.string(), z.null()]),
    appointment_type_name: z.enum(['Checkgesprek', 'Toekomstgesprek', 'SHVO intake']),
  })
  .passthrough()
const CasePublic = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    initial_appointment: z.union([AppointmentPublic, z.null()]),
  })
  .passthrough()
const ClientWithCasePublic = z
  .object({
    company_location: z.string().min(1),
    residence_location: z.string().min(1),
    initials: z.string().min(1),
    last_name_prefix: z.union([z.string(), z.null()]).optional(),
    last_name: z.string().min(1),
    company_name: z.union([z.string(), z.null()]).optional(),
    kvk_number: z.union([z.string(), z.null()]).optional(),
    bsn: z.string().min(1),
    phone_number: z.string().min(1),
    agree_to_share_data: z.boolean(),
    email: z.string().min(1),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    active_case: z.union([CasePublic, z.null()]).optional(),
  })
  .passthrough()
const ValidationError = z
  .object({ loc: z.array(z.union([z.string(), z.number()])), msg: z.string(), type: z.string() })
  .passthrough()
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough()
const ClientLocation = z
  .object({ company_location: z.string().min(1), residence_location: z.string().min(1) })
  .passthrough()
const ValidationResult = z.object({ errors: z.array(z.string()), valid: z.boolean() }).passthrough()
const ClientDetails = z
  .object({
    initials: z.string().min(1),
    last_name_prefix: z.union([z.string(), z.null()]).optional(),
    last_name: z.string().min(1),
    company_name: z.union([z.string(), z.null()]).optional(),
    kvk_number: z.union([z.string(), z.null()]).optional(),
    bsn: z.string().min(1),
    phone_number: z.string().min(1),
    agree_to_share_data: z.boolean(),
    email: z.string().min(1),
  })
  .passthrough()
const ClientNew = z.object({ location: ClientLocation, details: ClientDetails }).passthrough()
const Client = z
  .object({
    company_location: z.string().min(1),
    residence_location: z.string().min(1),
    initials: z.string().min(1),
    last_name_prefix: z.union([z.string(), z.null()]).optional(),
    last_name: z.string().min(1),
    company_name: z.union([z.string(), z.null()]).optional(),
    kvk_number: z.union([z.string(), z.null()]).optional(),
    bsn: z.string().min(1),
    phone_number: z.string().min(1),
    agree_to_share_data: z.boolean(),
    email: z.string().min(1),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough()
const client_id = z.union([z.string(), z.null()]).optional()
const AvailabilityDefined = z
  .object({ hour_start: z.number().int(), hour_end: z.number().int(), capacity: z.number().int() })
  .passthrough()
const AvailabilityDated = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    default: z.boolean(),
    date: z.union([z.string(), z.null()]),
    availability_slots_defined: z.array(AvailabilityDefined),
  })
  .passthrough()
const AvailabilityResponse = z
  .object({
    start_date: z.string(),
    end_date: z.string(),
    availability_defined_dated: z.array(AvailabilityDated),
    availability_defined_default: AvailabilityDated,
  })
  .passthrough()
const ClientUpdate = z.object({ location: ClientLocation, details: ClientDetails }).passthrough()
const ClientUpdateResponse = z.object({ message: z.union([z.string(), z.null()]) }).passthrough()
const UserCreated = z
  .object({
    password: z.string(),
    name: z.string(),
    has_email: z.boolean(),
    message: z.array(z.string()),
  })
  .passthrough()
const UserWithPermissions = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
    name: z.string(),
    permissions: z.array(
      z.enum([
        'appointment:create',
        'appointment:read',
        'appointment:update',
        'appointment:delete',
        'appointment:form:update-checkgesprek',
        'appointment:form:update-toekomstgesprek',
        'appointment:file:update',
        'appointment:file:create',
        'appointment:file:delete',
        'appointment:file:read',
        'appointment:update:status',
        'appointment:update:date',
        'availability:create',
        'availability:read',
        'availability:update',
        'availability:delete',
        'comment:read',
        'comment:create',
        'case:create',
        'case:read',
        'case:update',
        'case:delete',
        'case:file:read',
        'case:file:update',
        'case:file:create',
        'case:file:delete',
        'client:create',
        'client:read',
        'client:update',
        'client:delete',
        'client:create-user',
        'file:approve',
        'form:create',
        'form:read',
        'form:read-all',
        'form:update',
        'form:approve',
        'product-category:create',
        'product-category:read',
        'product-category:update',
        'product-category:delete',
        'product:create',
        'product:read',
        'product:update',
        'product:delete',
        'role:create',
        'role:read',
        'role:update',
        'role:delete',
        'request:create',
        'request:read',
        'request:update',
        'request:delete',
        'task:read',
        'task:update',
        'task:create',
        'task:delete',
        'task:update:case',
        'task:update:completion-status',
        'track:create',
        'track:read',
        'track:update',
        'track:update:status',
        'track:update:completion_approval',
        'track:update:partner',
        'track:update:product',
        'track:update:product-category',
        'track:send-notification:partner-request',
        'track:form:update-eindevaluatie-adviseur',
        'track:form:update-eindevaluatie-partnerorganisatie',
        'track:form:update-volggesprek',
        'track:file:create',
        'track:file:update',
        'track:file:delete',
        'track:file:read',
        'track:delete',
        'user:create',
        'user:update',
        'user:delete',
        'user:read',
        'user-basic:read',
        'partner-organization:read',
        'partner-organization:create',
        'partner-organization:update',
        'partner-organization:delete',
      ])
    ),
  })
  .passthrough()
const ClientInternal = z
  .object({
    company_location: z.string().min(1),
    residence_location: z.string().min(1),
    initials: z.string().min(1),
    last_name_prefix: z.union([z.string(), z.null()]).optional(),
    last_name: z.string().min(1),
    company_name: z.union([z.string(), z.null()]).optional(),
    kvk_number: z.union([z.string(), z.null()]).optional(),
    bsn: z.string().min(1),
    phone_number: z.string().min(1),
    agree_to_share_data: z.boolean(),
    email: z.string().min(1),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    user: z.union([UserWithPermissions, z.null()]),
  })
  .passthrough()
const UserBase = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
    name: z.string(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough()
const CaseWithClientAndAdvisor = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    client: ClientInternal,
    case_number: z.number().int(),
    client_bsn: z.string(),
    client_last_name: z.string(),
    client_initials: z.string(),
    advisor: z.union([UserBase, z.null()]),
    advisor_name: z.union([z.string(), z.null()]),
    is_active: z.boolean(),
    client_company_name: z.union([z.string(), z.null()]),
    client_email: z.string(),
  })
  .passthrough()
const Case = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    client: ClientInternal,
    case_number: z.number().int(),
    client_bsn: z.string(),
    client_last_name: z.string(),
    client_initials: z.string(),
    advisor: z.union([UserBase, z.null()]),
    advisor_name: z.union([z.string(), z.null()]),
    is_active: z.boolean(),
    description: z.string(),
    client_company_name: z.union([z.string(), z.null()]),
    client_email: z.string(),
  })
  .passthrough()
const Role = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
  })
  .passthrough()
const User = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
    name: z.string(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    permissions: z.array(
      z.enum([
        'appointment:create',
        'appointment:read',
        'appointment:update',
        'appointment:delete',
        'appointment:form:update-checkgesprek',
        'appointment:form:update-toekomstgesprek',
        'appointment:file:update',
        'appointment:file:create',
        'appointment:file:delete',
        'appointment:file:read',
        'appointment:update:status',
        'appointment:update:date',
        'availability:create',
        'availability:read',
        'availability:update',
        'availability:delete',
        'comment:read',
        'comment:create',
        'case:create',
        'case:read',
        'case:update',
        'case:delete',
        'case:file:read',
        'case:file:update',
        'case:file:create',
        'case:file:delete',
        'client:create',
        'client:read',
        'client:update',
        'client:delete',
        'client:create-user',
        'file:approve',
        'form:create',
        'form:read',
        'form:read-all',
        'form:update',
        'form:approve',
        'product-category:create',
        'product-category:read',
        'product-category:update',
        'product-category:delete',
        'product:create',
        'product:read',
        'product:update',
        'product:delete',
        'role:create',
        'role:read',
        'role:update',
        'role:delete',
        'request:create',
        'request:read',
        'request:update',
        'request:delete',
        'task:read',
        'task:update',
        'task:create',
        'task:delete',
        'task:update:case',
        'task:update:completion-status',
        'track:create',
        'track:read',
        'track:update',
        'track:update:status',
        'track:update:completion_approval',
        'track:update:partner',
        'track:update:product',
        'track:update:product-category',
        'track:send-notification:partner-request',
        'track:form:update-eindevaluatie-adviseur',
        'track:form:update-eindevaluatie-partnerorganisatie',
        'track:form:update-volggesprek',
        'track:file:create',
        'track:file:update',
        'track:file:delete',
        'track:file:read',
        'track:delete',
        'user:create',
        'user:update',
        'user:delete',
        'user:read',
        'user-basic:read',
        'partner-organization:read',
        'partner-organization:create',
        'partner-organization:update',
        'partner-organization:delete',
      ])
    ),
    role: Role,
  })
  .passthrough()
const UserCreate = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
    name: z.string(),
  })
  .passthrough()
const UserUpdate = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
  })
  .passthrough()
const UserPasswordUpdate = z.object({ password: z.string() }).passthrough()
const Body_upload_file_api_file__post = z.object({ file: z.instanceof(File) }).passthrough()
const FileBase = z
  .object({
    description: z.union([z.string(), z.null()]),
    approved: z.boolean(),
    file_type: z.enum(['Plan van aanpak', 'Overig']),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    filename: z.string(),
    approval_required: z.boolean(),
  })
  .passthrough()
const FileUpdate = z
  .object({
    description: z.union([z.string(), z.null()]),
    approved: z.boolean(),
    file_type: z.enum(['Plan van aanpak', 'Overig']),
  })
  .passthrough()
const PartnerOrganization = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    name: z.string(),
    product_names: z.array(z.string()),
    description: z.union([z.string(), z.null()]),
    description_short: z.union([z.string(), z.null()]),
    product_category_names: z.array(z.string()),
  })
  .passthrough()
const TrackValues = z
  .object({
    track_type: z.array(z.string()),
    partner_organization: z.array(PartnerOrganization),
    completion_causes: z.array(z.string()),
    status: z.array(z.enum(['Nog niet gestart', 'Gestart', 'Beëindigd'])),
  })
  .passthrough()
const TrackCreate = z
  .object({
    track_type_name: z.enum(['Ondernemersdienstverlening', 'SHVO']),
    partner_organization_name: z.union([z.string(), z.null()]),
    priority: z.union([z.enum(['Crisis', 'Regulier']), z.null()]).optional(),
    product_name: z.union([z.string(), z.null()]).optional(),
    product_category_name: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.enum(['Nog niet gestart', 'Gestart', 'Beëindigd']), z.null()]).optional(),
    completion_cause: z.union([z.string(), z.null()]),
    completion_approved: z.boolean().optional().default(false),
  })
  .passthrough()
const RequiredFormTemplate = z
  .object({
    name: z.enum([
      'Checkgesprek',
      'Volgrapport',
      'Eindevaluatie door partner',
      'Eindevaluatie door adviseur',
      'Toekomstgesprek',
      'IOAZ-aanvraag',
      'BBZ-aanvraag',
      'BBZ-verlenging-aanvraag',
    ]),
    required_permission: z.enum([
      'appointment:create',
      'appointment:read',
      'appointment:update',
      'appointment:delete',
      'appointment:form:update-checkgesprek',
      'appointment:form:update-toekomstgesprek',
      'appointment:file:update',
      'appointment:file:create',
      'appointment:file:delete',
      'appointment:file:read',
      'appointment:update:status',
      'appointment:update:date',
      'availability:create',
      'availability:read',
      'availability:update',
      'availability:delete',
      'comment:read',
      'comment:create',
      'case:create',
      'case:read',
      'case:update',
      'case:delete',
      'case:file:read',
      'case:file:update',
      'case:file:create',
      'case:file:delete',
      'client:create',
      'client:read',
      'client:update',
      'client:delete',
      'client:create-user',
      'file:approve',
      'form:create',
      'form:read',
      'form:read-all',
      'form:update',
      'form:approve',
      'product-category:create',
      'product-category:read',
      'product-category:update',
      'product-category:delete',
      'product:create',
      'product:read',
      'product:update',
      'product:delete',
      'role:create',
      'role:read',
      'role:update',
      'role:delete',
      'request:create',
      'request:read',
      'request:update',
      'request:delete',
      'task:read',
      'task:update',
      'task:create',
      'task:delete',
      'task:update:case',
      'task:update:completion-status',
      'track:create',
      'track:read',
      'track:update',
      'track:update:status',
      'track:update:completion_approval',
      'track:update:partner',
      'track:update:product',
      'track:update:product-category',
      'track:send-notification:partner-request',
      'track:form:update-eindevaluatie-adviseur',
      'track:form:update-eindevaluatie-partnerorganisatie',
      'track:form:update-volggesprek',
      'track:file:create',
      'track:file:update',
      'track:file:delete',
      'track:file:read',
      'track:delete',
      'user:create',
      'user:update',
      'user:delete',
      'user:read',
      'user-basic:read',
      'partner-organization:read',
      'partner-organization:create',
      'partner-organization:update',
      'partner-organization:delete',
    ]),
  })
  .passthrough()
const FormStatus = z.enum(['Ingediend', 'Goedgekeurd', 'Gestart'])
const FormData = z
  .object({
    payload: z.union([z.object({}).partial().passthrough(), z.null()]),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    form_template_name: z.enum([
      'Checkgesprek',
      'Volgrapport',
      'Eindevaluatie door partner',
      'Eindevaluatie door adviseur',
      'Toekomstgesprek',
      'IOAZ-aanvraag',
      'BBZ-aanvraag',
      'BBZ-verlenging-aanvraag',
    ]),
    approval_required: z.boolean(),
    has_valid_payload: z.boolean(),
    approved: z.boolean(),
    submitted: z.boolean(),
    status: FormStatus,
    form_link_type: z.union([z.enum(['appointment', 'request', 'track']), z.null()]),
    case_id: z.union([z.string(), z.null()]),
    appointment_id: z.union([z.string(), z.null()]),
    track_id: z.union([z.string(), z.null()]),
    request_id: z.union([z.string(), z.null()]),
    case_description: z.union([z.string(), z.null()]),
    visible_payload: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .passthrough()
const CaseBase = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough()
const TrackBase = z
  .object({
    track_type_name: z.enum(['Ondernemersdienstverlening', 'SHVO']),
    partner_organization_name: z.union([z.string(), z.null()]),
    priority: z.union([z.enum(['Crisis', 'Regulier']), z.null()]).optional(),
    product_name: z.union([z.string(), z.null()]).optional(),
    product_category_name: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.enum(['Nog niet gestart', 'Gestart', 'Beëindigd']), z.null()]).optional(),
    completion_cause: z.union([z.string(), z.null()]),
    completion_approved: z.boolean().optional().default(false),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    start_dt: z.union([z.string(), z.null()]),
    end_dt: z.union([z.string(), z.null()]),
    required_forms: z.array(RequiredFormTemplate),
    forms: z.array(FormData),
    required_file_types: z.array(z.enum(['Plan van aanpak', 'Overig'])),
    case_id: z.string().uuid(),
  })
  .passthrough()
const AppointmentBase = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    start_time: z.union([z.string(), z.null()]),
    end_time: z.union([z.string(), z.null()]),
    forms: z.array(FormData),
    partner_organization_name: z.union([z.string(), z.null()]),
    status: z.enum(['Open', 'Voltooid', 'Geannuleerd']),
    required_forms: z.array(RequiredFormTemplate),
    track: z.union([TrackBase, z.null()]),
    case_id: z.string().uuid(),
    appointment_type_name: z.enum(['Checkgesprek', 'Toekomstgesprek', 'SHVO intake']),
  })
  .passthrough()
const Track = z
  .object({
    track_type_name: z.enum(['Ondernemersdienstverlening', 'SHVO']),
    partner_organization_name: z.union([z.string(), z.null()]),
    priority: z.union([z.enum(['Crisis', 'Regulier']), z.null()]).optional(),
    product_name: z.union([z.string(), z.null()]).optional(),
    product_category_name: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.enum(['Nog niet gestart', 'Gestart', 'Beëindigd']), z.null()]).optional(),
    completion_cause: z.union([z.string(), z.null()]),
    completion_approved: z.boolean().optional().default(false),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    start_dt: z.union([z.string(), z.null()]),
    end_dt: z.union([z.string(), z.null()]),
    required_forms: z.array(RequiredFormTemplate),
    forms: z.array(FormData),
    required_file_types: z.array(z.enum(['Plan van aanpak', 'Overig'])),
    case_id: z.string().uuid(),
    case: CaseBase,
    appointments: z.array(AppointmentBase),
    case_number: z.number().int(),
    client_initials: z.string(),
    client_last_name: z.string(),
    client_residence_location: z.string(),
    client_phone_number: z.union([z.string(), z.null()]),
    client_email: z.string(),
  })
  .passthrough()
const TrackUpdate = z
  .object({
    track_type_name: z.enum(['Ondernemersdienstverlening', 'SHVO']),
    partner_organization_name: z.union([z.string(), z.null()]),
    priority: z.union([z.enum(['Crisis', 'Regulier']), z.null()]).optional(),
    product_name: z.union([z.string(), z.null()]).optional(),
    product_category_name: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.enum(['Nog niet gestart', 'Gestart', 'Beëindigd']), z.null()]).optional(),
    completion_cause: z.union([z.string(), z.null()]),
    completion_approved: z.boolean().optional().default(false),
  })
  .passthrough()
const AppintmentSlotWithAvailability = z
  .object({
    start_time: z.string().datetime({ offset: true }),
    end_time: z.string().datetime({ offset: true }),
    has_advisor_available: z.boolean(),
  })
  .passthrough()
const TenantConfig = z
  .object({
    primary_color: z.string(),
    allowed_gemeentes: z.array(z.string()),
    residence_locations: z.array(z.string()),
    company_locations: z.array(z.string()),
  })
  .passthrough()
const AppConfig = z
  .object({
    keycloak_uri: z.string(),
    keycloak_realm: z.string(),
    keycloak_client_id: z.string(),
    app_version: z.string(),
    tenant_name: z.string(),
    tenant_config: TenantConfig,
    required_products: z.array(z.enum(['Toekomstgesprek', 'SHVO intake'])),
  })
  .passthrough()
const AppointmentNew = z
  .object({
    start_time: z.union([z.string(), z.null()]),
    end_time: z.union([z.string(), z.null()]),
    appointment_type_name: z.enum(['Checkgesprek', 'Toekomstgesprek', 'SHVO intake']),
    partner_organization_name: z.union([z.string(), z.null()]),
    status: z.enum(['Open', 'Voltooid', 'Geannuleerd']),
  })
  .passthrough()
const Appointment = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    start_time: z.union([z.string(), z.null()]),
    end_time: z.union([z.string(), z.null()]),
    forms: z.array(FormData),
    partner_organization_name: z.union([z.string(), z.null()]),
    status: z.enum(['Open', 'Voltooid', 'Geannuleerd']),
    required_forms: z.array(RequiredFormTemplate),
    track: z.union([TrackBase, z.null()]),
    case_id: z.string().uuid(),
    case_number: z.number().int(),
    client_initials: z.string(),
    client_last_name: z.string(),
    client_residence_location: z.string(),
    client_phone_number: z.union([z.string(), z.null()]),
    client_email: z.string(),
    appointment_type_name: z.enum(['Checkgesprek', 'Toekomstgesprek', 'SHVO intake']),
  })
  .passthrough()
const AppointmentUpdate = z
  .object({
    start_time: z.union([z.string(), z.null()]),
    end_time: z.union([z.string(), z.null()]),
    appointment_type_name: z.enum(['Checkgesprek', 'Toekomstgesprek', 'SHVO intake']),
    partner_organization_name: z.union([z.string(), z.null()]),
    status: z.enum(['Open', 'Voltooid', 'Geannuleerd']),
  })
  .passthrough()
const TaskStatus = z.enum(['Openstaand', 'In uitvoering', 'Gesloten'])
const Task = z
  .object({
    status: TaskStatus,
    description: z.string(),
    due_date: z.string().datetime({ offset: true }),
    case_id: z.string().uuid(),
    user_id: z.union([z.string(), z.null()]),
    completed: z.boolean(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    is_due: z.boolean(),
    user: z.union([User, z.null()]),
    user_name: z.union([z.string(), z.null()]),
    case: CaseBase,
    case_number: z.number().int(),
  })
  .passthrough()
const TaskUpsert = z
  .object({
    status: TaskStatus,
    description: z.string(),
    due_date: z.string().datetime({ offset: true }),
    case_id: z.string().uuid(),
    user_id: z.union([z.string(), z.null()]),
    completed: z.boolean(),
  })
  .passthrough()
const PayloadValidationError = z
  .object({
    message: z.string(),
    absolute_schema_path: z.array(z.union([z.string(), z.number()])),
    validator: z.union([
      z.enum([
        '$recursiveRef',
        '$ref',
        'additionalItems',
        'additionalProperties',
        'allOf',
        'anyOf',
        'const',
        'contains',
        'dependentRequired',
        'dependentSchemas',
        'enum',
        'exclusiveMaximum',
        'exclusiveMinimum',
        'format',
        'if',
        'items',
        'maxItems',
        'maxLength',
        'maxProperties',
        'maximum',
        'minItems',
        'minLength',
        'minProperties',
        'minimum',
        'multipleOf',
        'not',
        'oneOf',
        'pattern',
        'patternProperties',
        'properties',
        'propertyNames',
        'required',
        'type',
        'unevaluatedItems',
        'unevaluatedProperties',
        'uniqueItems',
      ]),
      z.null(),
    ]),
    readable_message: z.string(),
  })
  .passthrough()
const PayloadValidation = z
  .object({
    is_valid: z.boolean(),
    validation_errors: z.array(PayloadValidationError),
    required_properties: z.array(z.string()),
  })
  .passthrough()
const FormTemplate = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    name: z.enum([
      'Checkgesprek',
      'Volgrapport',
      'Eindevaluatie door partner',
      'Eindevaluatie door adviseur',
      'Toekomstgesprek',
      'IOAZ-aanvraag',
      'BBZ-aanvraag',
      'BBZ-verlenging-aanvraag',
    ]),
    template_schema: z.object({}).partial().passthrough(),
  })
  .passthrough()
const FormDataUpsert = z
  .object({ payload: z.union([z.object({}).partial().passthrough(), z.null()]) })
  .passthrough()
const Product = z
  .object({
    name: z.string(),
    code: z.union([z.string(), z.null()]),
    product_category_name: z.string(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    product_category_id: z.string().uuid(),
  })
  .passthrough()
const ProductCategory = z
  .object({
    name: z.string(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    products: z.array(Product),
  })
  .passthrough()
const ProductCategoryCreate = z.object({ name: z.string() }).passthrough()
const ProductCategoryUpdate = z.object({ name: z.string() }).passthrough()
const ProductCreate = z
  .object({
    name: z.string(),
    code: z.union([z.string(), z.null()]),
    product_category_name: z.string(),
  })
  .passthrough()
const ProductUpdate = z
  .object({
    name: z.string(),
    code: z.union([z.string(), z.null()]),
    product_category_name: z.string(),
  })
  .passthrough()
const PartnerOrganizationUpsert = z
  .object({
    name: z.string(),
    product_names: z.array(z.string()),
    description: z.union([z.string(), z.null()]),
    description_short: z.union([z.string(), z.null()]),
  })
  .passthrough()
const RequestUpsert = z
  .object({ name: z.enum(['IOAZ-aanvraag', 'BBZ-aanvraag', 'BBZ-verlenging-aanvraag']) })
  .passthrough()
const Request = z
  .object({
    name: z.enum(['IOAZ-aanvraag', 'BBZ-aanvraag', 'BBZ-verlenging-aanvraag']),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    form: FormData,
    form_is_completed: z.boolean(),
  })
  .passthrough()
const Body_validate_json_schema_api_json_schema_validation__post = z
  .object({
    jsonschema: z.object({}).partial().passthrough(),
    payload: z.object({}).partial().passthrough(),
  })
  .passthrough()
const PayloadValidationWrapper = z
  .object({
    is_valid: z.boolean(),
    validation_errors: z.array(PayloadValidationError),
    required_properties: z.array(z.string()),
  })
  .passthrough()
const Comment = z
  .object({
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    content: z.string(),
    created_by_user: UserBase,
    comment_thread_id: z.string().uuid(),
  })
  .passthrough()
const UserWithCase = z
  .object({
    role_name: z.enum(['beheerder', 'senioradviseur', 'adviseur', 'partner', 'ondernemer']),
    partner_organization_name: z.union([z.string(), z.null()]),
    active: z.boolean(),
    name: z.string(),
    id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    permissions: z.array(
      z.enum([
        'appointment:create',
        'appointment:read',
        'appointment:update',
        'appointment:delete',
        'appointment:form:update-checkgesprek',
        'appointment:form:update-toekomstgesprek',
        'appointment:file:update',
        'appointment:file:create',
        'appointment:file:delete',
        'appointment:file:read',
        'appointment:update:status',
        'appointment:update:date',
        'availability:create',
        'availability:read',
        'availability:update',
        'availability:delete',
        'comment:read',
        'comment:create',
        'case:create',
        'case:read',
        'case:update',
        'case:delete',
        'case:file:read',
        'case:file:update',
        'case:file:create',
        'case:file:delete',
        'client:create',
        'client:read',
        'client:update',
        'client:delete',
        'client:create-user',
        'file:approve',
        'form:create',
        'form:read',
        'form:read-all',
        'form:update',
        'form:approve',
        'product-category:create',
        'product-category:read',
        'product-category:update',
        'product-category:delete',
        'product:create',
        'product:read',
        'product:update',
        'product:delete',
        'role:create',
        'role:read',
        'role:update',
        'role:delete',
        'request:create',
        'request:read',
        'request:update',
        'request:delete',
        'task:read',
        'task:update',
        'task:create',
        'task:delete',
        'task:update:case',
        'task:update:completion-status',
        'track:create',
        'track:read',
        'track:update',
        'track:update:status',
        'track:update:completion_approval',
        'track:update:partner',
        'track:update:product',
        'track:update:product-category',
        'track:send-notification:partner-request',
        'track:form:update-eindevaluatie-adviseur',
        'track:form:update-eindevaluatie-partnerorganisatie',
        'track:form:update-volggesprek',
        'track:file:create',
        'track:file:update',
        'track:file:delete',
        'track:file:read',
        'track:delete',
        'user:create',
        'user:update',
        'user:delete',
        'user:read',
        'user-basic:read',
        'partner-organization:read',
        'partner-organization:create',
        'partner-organization:update',
        'partner-organization:delete',
      ])
    ),
    role: Role,
    active_case_id: z.union([z.string(), z.null()]),
  })
  .passthrough()

export const schemas = {
  AppointmentPublic,
  CasePublic,
  ClientWithCasePublic,
  ValidationError,
  HTTPValidationError,
  ClientLocation,
  ValidationResult,
  ClientDetails,
  ClientNew,
  Client,
  client_id,
  AvailabilityDefined,
  AvailabilityDated,
  AvailabilityResponse,
  ClientUpdate,
  ClientUpdateResponse,
  UserCreated,
  UserWithPermissions,
  ClientInternal,
  UserBase,
  CaseWithClientAndAdvisor,
  Case,
  Role,
  User,
  UserCreate,
  UserUpdate,
  UserPasswordUpdate,
  Body_upload_file_api_file__post,
  FileBase,
  FileUpdate,
  PartnerOrganization,
  TrackValues,
  TrackCreate,
  RequiredFormTemplate,
  FormStatus,
  FormData,
  CaseBase,
  TrackBase,
  AppointmentBase,
  Track,
  TrackUpdate,
  AppintmentSlotWithAvailability,
  TenantConfig,
  AppConfig,
  AppointmentNew,
  Appointment,
  AppointmentUpdate,
  TaskStatus,
  Task,
  TaskUpsert,
  PayloadValidationError,
  PayloadValidation,
  FormTemplate,
  FormDataUpsert,
  Product,
  ProductCategory,
  ProductCategoryCreate,
  ProductCategoryUpdate,
  ProductCreate,
  ProductUpdate,
  PartnerOrganizationUpsert,
  RequestUpsert,
  Request,
  Body_validate_json_schema_api_json_schema_validation__post,
  PayloadValidationWrapper,
  Comment,
  UserWithCase,
}

const endpoints = makeApi([
  {
    method: 'get',
    path: '/api/',
    alias: 'root_api__get',
    requestFormat: 'json',
    response: z.unknown(),
  },
  {
    method: 'post',
    path: '/api/appointment-public/',
    alias: 'create_initial_appointment_api_appointment_public__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'start_time',
        type: 'Query',
        schema: z.string().datetime({ offset: true }),
      },
      {
        name: 'end_time',
        type: 'Query',
        schema: z.string().datetime({ offset: true }),
      },
      {
        name: 'token',
        type: 'Query',
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/appointment-slot/',
    alias: 'get_available_slots_api_appointment_slot__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'start_date',
        type: 'Query',
        schema: z.string(),
      },
      {
        name: 'end_date',
        type: 'Query',
        schema: z.string(),
      },
    ],
    response: z.array(AppintmentSlotWithAvailability),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/appointment/',
    alias: 'create_appointment_api_appointment__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: AppointmentNew,
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/appointment/',
    alias: 'get_appointments_api_appointment__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(Appointment),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/appointment/:appointment_id',
    alias: 'delete_appointment_api_appointment__appointment_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'appointment_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/appointment/:appointment_id',
    alias: 'update_appointment_api_appointment__appointment_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: AppointmentUpdate,
      },
      {
        name: 'appointment_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/appointment/:appointment_id',
    alias: 'fetch_appointment_api_appointment__appointment_id__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'appointment_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: Appointment,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/availability/',
    alias: 'get_availability_api_availability__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'start_date',
        type: 'Query',
        schema: z.string(),
      },
      {
        name: 'end_date',
        type: 'Query',
        schema: z.string(),
      },
    ],
    response: AvailabilityResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'patch',
    path: '/api/availability/:date/slot/:hour_start',
    alias: 'update_availability_api_availability__date__slot__hour_start__patch',
    requestFormat: 'json',
    parameters: [
      {
        name: 'date',
        type: 'Path',
        schema: z.string(),
      },
      {
        name: 'hour_start',
        type: 'Path',
        schema: z.number().int(),
      },
      {
        name: 'new_capacity',
        type: 'Query',
        schema: z.number().int(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/case/',
    alias: 'get_cases_api_case__get',
    requestFormat: 'json',
    response: z.array(CaseWithClientAndAdvisor),
  },
  {
    method: 'get',
    path: '/api/case/:case_id',
    alias: 'fetch_case_api_case__case_id__get',
    description: `Returns the case with its related tracks, appointments and tasks.`,
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: Case,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/case/:case_id',
    alias: 'delete_case_api_case__case_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'patch',
    path: '/api/case/:case_id/advisor',
    alias: 'update_case_advisor_api_case__case_id__advisor_patch',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'advisor_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/case/:case_id/request',
    alias: 'create_request_api_case__case_id__request_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: RequestUpsert,
      },
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/case/:case_id/request/',
    alias: 'get_requests_api_case__case_id__request__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.array(Request),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/case/:case_id/request/:request_id',
    alias: 'update_request_api_case__case_id__request__request_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: RequestUpsert,
      },
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'request_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/case/:case_id/request/:request_id',
    alias: 'delete_request_api_case__case_id__request__request_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'request_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/case/:case_id/track',
    alias: 'create_track_api_case__case_id__track_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: TrackCreate,
      },
      {
        name: 'case_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/case/:case_id/track/:track_id',
    alias: 'delete_track_api_case__case_id__track__track_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'track_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/case/:case_id/track/:track_id',
    alias: 'update_track_api_case__case_id__track__track_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: TrackUpdate,
      },
      {
        name: 'track_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/client/',
    alias: 'create_client_api_client__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: ClientNew,
      },
    ],
    response: Client,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/client/:client_id',
    alias: 'fetch_client_api_client__client_id__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'client_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: Client,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/client/:client_id',
    alias: 'update_client_api_client__client_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: ClientUpdate,
      },
      {
        name: 'client_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: ClientUpdateResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/client/:client_id/confirm-email',
    alias: 'confirm_email_api_client__client_id__confirm_email_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'token',
        type: 'Query',
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/client/:client_id/user',
    alias: 'create_user_api_client__client_id__user_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'client_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: UserCreated,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/client/client-from-token',
    alias: 'validate_token_api_client_client_from_token_get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'token',
        type: 'Query',
        schema: z.string(),
      },
    ],
    response: ClientWithCasePublic,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/client/resend-confirmation-request',
    alias: 'send_confirmation_api_client_resend_confirmation_request_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'client_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'email',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/client/validation',
    alias: 'create_validation_api_client_validation_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: ClientLocation,
      },
    ],
    response: ValidationResult,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/comment/',
    alias: 'create_comment_api_comment__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'content',
        type: 'Query',
        schema: z.string().min(3).max(1024),
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/comment/',
    alias: 'get_comments_api_comment__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(Comment),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/config/',
    alias: 'get_app_config_api_config__get',
    requestFormat: 'json',
    response: AppConfig,
  },
  {
    method: 'post',
    path: '/api/file/',
    alias: 'upload_file_api_file__post',
    requestFormat: 'form-data',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: z.object({ file: z.instanceof(File) }).passthrough(),
      },
      {
        name: 'file_type',
        type: 'Query',
        schema: z.enum(['Plan van aanpak', 'Overig']),
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/file/',
    alias: 'get_files_api_file__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(FileBase),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/file/:file_id',
    alias: 'download_file_api_file__file_id__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'file_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/file/:file_id',
    alias: 'update_file_api_file__file_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: FileUpdate,
      },
      {
        name: 'file_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/file/:file_id',
    alias: 'delete_file_api_file__file_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'file_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/form-data',
    alias: 'get_forms_api_form_data_get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'request_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(FormData),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/form-data/',
    alias: 'create_form_data_api_form_data__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: FormDataUpsert,
      },
      {
        name: 'form_name',
        type: 'Query',
        schema: z.enum([
          'Checkgesprek',
          'Volgrapport',
          'Eindevaluatie door partner',
          'Eindevaluatie door adviseur',
          'Toekomstgesprek',
          'IOAZ-aanvraag',
          'BBZ-aanvraag',
          'BBZ-verlenging-aanvraag',
        ]),
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'request_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: FormData,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/form-data/:form_data_id',
    alias: 'get_one_form_api_form_data__form_data_id__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'form_data_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: FormData,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/form-data/:form_data_id',
    alias: 'update_form_data_api_form_data__form_data_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: FormDataUpsert,
      },
      {
        name: 'form_data_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'track_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'appointment_id',
        type: 'Query',
        schema: client_id,
      },
      {
        name: 'request_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/form-data/:form_data_id/status/:form_status',
    alias: 'update_form_data_status_api_form_data__form_data_id__status__form_status__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'form_status',
        type: 'Path',
        schema: z.enum(['Ingediend', 'Goedgekeurd', 'Gestart']),
      },
      {
        name: 'form_data_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/form-template/:form_name',
    alias: 'get_form_template_api_form_template__form_name__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'form_name',
        type: 'Path',
        schema: z.enum([
          'Checkgesprek',
          'Volgrapport',
          'Eindevaluatie door partner',
          'Eindevaluatie door adviseur',
          'Toekomstgesprek',
          'IOAZ-aanvraag',
          'BBZ-aanvraag',
          'BBZ-verlenging-aanvraag',
        ]),
      },
    ],
    response: FormTemplate,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/form-template/:form_name/validation',
    alias: 'validate_form_template_api_form_template__form_name__validation_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: 'form_name',
        type: 'Path',
        schema: z.enum([
          'Checkgesprek',
          'Volgrapport',
          'Eindevaluatie door partner',
          'Eindevaluatie door adviseur',
          'Toekomstgesprek',
          'IOAZ-aanvraag',
          'BBZ-aanvraag',
          'BBZ-verlenging-aanvraag',
        ]),
      },
    ],
    response: PayloadValidation,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/json-schema-validation/',
    alias: 'validate_json_schema_api_json_schema_validation__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: Body_validate_json_schema_api_json_schema_validation__post,
      },
    ],
    response: PayloadValidationWrapper,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/me',
    alias: 'get_me_api_me_get',
    requestFormat: 'json',
    response: UserWithCase,
  },
  {
    method: 'get',
    path: '/api/partner-organization/',
    alias: 'fetch_partner_organizations_api_partner_organization__get',
    requestFormat: 'json',
    response: z.array(PartnerOrganization),
  },
  {
    method: 'post',
    path: '/api/partner-organization/',
    alias: 'create_partner_organization_api_partner_organization__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: PartnerOrganizationUpsert,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/partner-organization/:partner_organization_id',
    alias: 'update_partner_organization_api_partner_organization__partner_organization_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: PartnerOrganizationUpsert,
      },
      {
        name: 'partner_organization_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/partner-organization/:partner_organization_id',
    alias: 'delete_partner_organization_api_partner_organization__partner_organization_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'partner_organization_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/product-category/',
    alias: 'get_cases_api_product_category__get',
    requestFormat: 'json',
    response: z.array(ProductCategory),
  },
  {
    method: 'post',
    path: '/api/product-category/',
    alias: 'create_product_category_api_product_category__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: z.object({ name: z.string() }).passthrough(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/product-category/:product_category_id',
    alias: 'update_product_category_api_product_category__product_category_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: z.object({ name: z.string() }).passthrough(),
      },
      {
        name: 'product_category_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/product-category/:product_category_id',
    alias: 'delete_product_category_api_product_category__product_category_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'product_category_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/product/',
    alias: 'get_products_api_product__get',
    requestFormat: 'json',
    response: z.array(Product),
  },
  {
    method: 'post',
    path: '/api/product/',
    alias: 'create_product_api_product__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: ProductCreate,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/product/:product_id',
    alias: 'update_product_api_product__product_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: ProductUpdate,
      },
      {
        name: 'product_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/product/:product_id',
    alias: 'delete_product_api_product__product_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'product_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/role/',
    alias: 'get_cases_api_role__get',
    requestFormat: 'json',
    response: z.array(Role),
  },
  {
    method: 'get',
    path: '/api/task/',
    alias: 'get_tasks_api_task__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(Task),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/task/',
    alias: 'create_task_api_task__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: TaskUpsert,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/task/:task_id',
    alias: 'update_task_api_task__task_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: TaskUpsert,
      },
      {
        name: 'task_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/task/:task_id',
    alias: 'delete_task_api_task__task_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'task_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/track',
    alias: 'get_tracks_api_track_get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(Track),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/track-value/',
    alias: 'fetch_track_types_api_track_value__get',
    requestFormat: 'json',
    response: TrackValues,
  },
  {
    method: 'get',
    path: '/api/track/:track_id',
    alias: 'get_track_api_track__track_id__get',
    requestFormat: 'json',
    parameters: [
      {
        name: 'track_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: Track,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/track/:track_id/partner-organization-choice-request',
    alias:
      'request_partner_organization_choice_api_track__track_id__partner_organization_choice_request_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'track_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.string(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'patch',
    path: '/api/track/:track_id/partner-organization/:partner_organization_name',
    alias:
      'update_track_partner_organization_api_track__track_id__partner_organization__partner_organization_name__patch',
    requestFormat: 'json',
    parameters: [
      {
        name: 'track_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
      {
        name: 'partner_organization_name',
        type: 'Path',
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/user-basic/',
    alias: 'get_users_basic_api_user_basic__get',
    description: `Returns a list of users with minimal information, suitable for basic user selection.`,
    requestFormat: 'json',
    parameters: [
      {
        name: 'case_id',
        type: 'Query',
        schema: client_id,
      },
    ],
    response: z.array(UserBase),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'get',
    path: '/api/user/',
    alias: 'get_users_api_user__get',
    requestFormat: 'json',
    response: z.array(User),
  },
  {
    method: 'post',
    path: '/api/user/',
    alias: 'create_user_api_user__post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: UserCreate,
      },
    ],
    response: UserCreated,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'put',
    path: '/api/user/:user_id',
    alias: 'update_user_api_user__user_id__put',
    requestFormat: 'json',
    parameters: [
      {
        name: 'body',
        type: 'Body',
        schema: UserUpdate,
      },
      {
        name: 'user_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: User,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'delete',
    path: '/api/user/:user_id',
    alias: 'delete_user_api_user__user_id__delete',
    requestFormat: 'json',
    parameters: [
      {
        name: 'user_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: 'post',
    path: '/api/user/:user_id/reset-password',
    alias: 'reset_password_api_user__user_id__reset_password_post',
    requestFormat: 'json',
    parameters: [
      {
        name: 'user_id',
        type: 'Path',
        schema: z.string().uuid(),
      },
    ],
    response: z.object({ password: z.string() }).passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
])

export const api = new Zodios(endpoints)

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options)
}
