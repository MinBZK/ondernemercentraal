import type { components } from '@/api/schema'

type Client = components['schemas']['Client']
type Track = components['schemas']['Track']
type Form = components['schemas']['FormData']
type Task = components['schemas']['Task']

export function useEntityLabels() {
  const { t } = useLocale()

  const clientLabels: EntityLabelDictionary<Client> = {
    agree_to_share_data: () => t('entityAttributes.client.agreeToShareData'),
    bsn: () => t('entityAttributes.client.bsn'),
    company_location: () => t('entityAttributes.client.companyLocation'),
    company_name: () => t('entityAttributes.client.companyName'),
    email: () => t('entityAttributes.client.email'),
    initials: () => t('entityAttributes.client.initials'),
    kvk_number: () => t('entityAttributes.client.kvkNumber'),
    last_name: () => t('entityAttributes.client.lastName'),
    last_name_prefix: () => t('entityAttributes.client.lastNamePrefix'),
    phone_number: () => t('entityAttributes.client.phoneNumber'),
    residence_location: () => t('entityAttributes.client.residenceLocation'),
    id: () => t('common.id'),
    created_at: () => t('common.created_at'),
    updated_at: () => t('common.updated_at'),
  }

  const trackLabels: EntityLabelDictionary<Track> = {
    id: () => 'id',
    created_at: () => 'Aangemaakt op',
    end_dt: () => 'Einddatum',
    start_dt: () => 'Startdatum',
    status: () => 'Status',
    track_type_name: () => 'Type',
    partner_organization_name: () => 'Partnerorganisatie',
    updated_at: () => 'Laatst gewijzigd op',
    completion_cause: () => 'Beëindigingsreden',
    completion_approved: () => 'Beëindiging goedgekeurd',
    case: () => 'Dossier',
    required_forms: () => 'Vereiste formulieren',
    forms: () => 'Ingevulde formulieren',
    case_id: () => 'Dossier',
    priority: () => 'Urgentie',
    required_file_types: () => 'Benodigde bestanden',
    appointments: () => 'Gesprekken',
    product_name: () => 'Dienstverlening',
    case_number: () => 'Dossier',
    client_initials: () => 'Voorletters',
    client_last_name: () => 'Achternaam',
    client_residence_location: () => 'Woonplaats',
    client_phone_number: () => 'Telefoonnummer',
    client_email: () => 'E-mailadres',
    product_category_name: () => 'Pijler',
  }

  const formLabels: EntityLabelDictionary<Form> = {
    id: () => 'id',
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    payload: () => 'Inhoud',
    // form_template: () => 'Formulier template',
    form_template_name: () => 'Formuliernaam',
    approval_required: () => 'Goedkeuring vereist',
    approved: () => 'Goedkeuringsstatus',
    submitted: () => 'Ingediend',
    has_valid_payload: () => 'Volledig ingevuld',
    visible_payload: () => 'Relevante inhoud',
    status: () => 'Status',
    form_link_type: () => 'Gelinkt aan',
    appointment_id: () => 'Gesprek',
    track_id: () => 'Traject',
    case_id: () => 'Dossier',
    request_id: () => 'Verzoek',
    case_description: () => 'Dossier',
  }

  const taskLabels: EntityLabelDictionary<Task> = {
    id: () => 'id',
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    description: () => 'Omschrijving',
    due_date: () => 'Te voltooien per',
    status: () => 'Status',
    is_due: () => 'Is verlopen',
    user: () => 'Gebruiker',
    case_id: () => 'Dossier',
    user_id: () => 'Gebruikers id',
    user_name: () => 'Toegewezen aan',
    case: () => 'Dossier',
    completed: () => 'Afgerond',
    case_number: () => 'Dossier',
  }

  const appointmentLabels: EntityLabelDictionary<components['schemas']['Appointment']> = {
    appointment_type_name: () => 'Gesprekstype',
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    id: () => 'id',
    start_time: () => 'Startdatum',
    end_time: () => 'Einddatum',
    partner_organization_name: () => 'Partnerorganisatie',
    status: () => 'Status',
    required_forms: () => 'Formulieren',
    forms: () => 'Ingevulde formulieren',
    track: () => 'Traject',
    case_id: () => 'Dossier',
    client_email: () => 'E-mailadres',
    client_initials: () => 'Voorletters',
    client_last_name: () => 'Achternaam',
    client_residence_location: () => 'Woonplaats',
    client_phone_number: () => 'Telefoonnummer',
    case_number: () => 'Dossier',
  }

  const productCategoryLabels: EntityLabelDictionary<components['schemas']['ProductCategory']> = {
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    id: () => 'Id',
    name: () => 'Naam',
    products: () => 'Dienstverleningen',
  }

  const productLabels: EntityLabelDictionary<components['schemas']['Product']> = {
    name: () => 'Naam',
    id: () => 'Id',
    code: () => 'Aanmeldcode',
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    product_category_id: () => 'Pijler id',
    product_category_name: () => 'Pijler',
  }

  const partnerOrganizationLabels: EntityLabelDictionary<
    components['schemas']['PartnerOrganization']
  > = {
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    id: () => 'Id',
    name: () => 'Naam',
    description: () => 'Omschrijving',
    description_short: () => 'Korte omschrijving',
    product_names: () => 'Dienstverleningen',
    product_category_names: () => 'Pijlers',
  }

  const caseLabels: EntityLabelDictionary<components['schemas']['Case']> = {
    advisor: () => 'Adviseur',
    is_active: () => 'Actief',
    created_at: () => 'Aangemaakt op',
    updated_at: () => 'Laatst gewijzigd op',
    id: () => 'Id',
    client: () => 'Ondenemer',
    case_number: () => 'Dossier',
    client_bsn: () => 'BSN',
    client_last_name: () => 'Achternaam',
    client_initials: () => 'Voorletters',
    advisor_name: () => 'Naam adviseur',
    description: () => 'Omschrijving',
    client_company_name: () => 'Bedrijfsnaam',
    client_email: () => 'E-mailadres',
  }

  const userLabels: EntityLabelDictionary<components['schemas']['User']> = {
    active: () => 'Actief',
    name: () => 'Gebruikersnaam',
    partner_organization_name: () => 'Partnerorganisatie',
    created_at: () => 'Aangemaakt op',
    id: () => 'Id',
    permissions: () => 'Rechten',
    role: () => 'Rol',
    role_name: () => 'Rolnaam',
    updated_at: () => 'Laatst gewijzigd op',
  }

  const requestLabels: EntityLabelDictionary<components['schemas']['Request']> = {
    id: () => 'Id',
    created_at: () => 'Aangemaakt op',
    name: () => 'Naam',
    updated_at: () => 'Laatst gewijzigd op',
    form: () => 'Formulier',
    form_is_completed: () => 'Formulier volledig ingevuld',
    form_status: () => 'Status',
  }

  return {
    clientLabels,
    trackLabels,
    formLabels,
    taskLabels,
    appointmentLabels,
    productCategoryLabels,
    productLabels,
    caseLabels,
    partnerOrganizationLabels,
    userLabels,
    requestLabels,
  }
}
