import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalizedGeneric,
  type RouteLocationNormalizedLoadedGeneric,
} from 'vue-router'
import Unauthorized from '@/pages/Unauthorized.vue'
import AppointmentCrud from './views/AppointmentCrud.vue'
import BeheerCaseDetail from '@/pages/Beheer/BeheerCaseDetail.vue'
import DialogForm from './components/DialogForm.vue'
import TrackCrud from './views/TrackCrud.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/geen-toegang',
      name: 'Unauthorized',
      components: {
        error: Unauthorized,
      },
    },
    {
      path: '/',
      redirect: '/nl',
    },
    {
      path: '/:locale',
      component: () => import('@/layouts/LocaleLayout.vue'),
      children: [
        {
          path: '',
          name: 'Welkom',
          component: () => import('@/pages/Home.vue'),
          props: true,
        },
        {
          path: 'appointment/new',
          name: 'AppointmentCreate',
          component: () => import('@/pages/AppointmentCreateClient.vue'),
          props: true,
        },
        {
          path: 'appointment/client-created',
          name: 'AppointmentClientCreated',
          component: () => import('@/pages/AppointmentClientCreated.vue'),
        },
        {
          path: 'appointment/confirmed',
          name: 'AppointmentConfirmed',
          component: () => import('@/pages/AppointmentConfirmed.vue'),
          props: true,
        },
        {
          path: 'appointment/pick',
          name: 'AppointmentPick',
          component: () => import('@/pages/AppointmentCreateInitial.vue'),
        },
        {
          path: 'appointment',
          name: 'AppointmentMany',
          component: () => import('@/pages/AppointmentMany.vue'),
          props: true,
        },
        {
          path: 'client/confirm',
          name: 'ClientConfirmEmail',
          component: () => import('@/pages/ClientConfirmEmail.vue'),
        },
      ],
    },
    {
      path: '/beheer',
      component: () => import('@/components/layout/PageWithSidebar.vue'),
      children: [
        {
          name: 'Beheer',
          path: '',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer.vue'),
          props: false,
        },
        {
          path: 'availability',
          name: 'BeheerAvailability',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerAvailability.vue'),
        },
        {
          path: 'case',
          name: 'BeheerCaseMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerCaseMany.vue'),
        },
        {
          path: 'case/:caseId/',
          children: [
            {
              name: 'BeheerCaseDetail',
              path: '',
              beforeEnter: authGuard,
              component: BeheerCaseDetail,
              props: true,
            },
            {
              name: 'BeheerCaseAppointmentCreate',
              path: 'appointment/',
              beforeEnter: authGuard,
              components: {
                default: BeheerCaseDetail,
                modal: AppointmentCrud,
              },
              props: true,
            },
            {
              name: 'BeheerCaseAppointmentDetail',
              path: 'appointment/:appointmentId',
              beforeEnter: authGuard,
              components: {
                default: BeheerCaseDetail,
                modal: AppointmentCrud,
              },
              props: true,
              children: [
                {
                  path: 'create-form/:formTemplateName',
                  name: 'BeheerAppointmentFormCreate',
                  components: {
                    default: BeheerCaseDetail,
                    nestedForm: DialogForm,
                  },
                  props: {
                    default: true,
                    nestedForm: true,
                  },
                },
                {
                  path: 'form-data/:formDataId',
                  name: 'BeheerAppointmentFormData',
                  components: {
                    default: BeheerCaseDetail,
                    nestedForm: DialogForm,
                  },
                  props: {
                    default: true,
                    nestedForm: true,
                  },
                },
              ],
            },
            {
              name: 'BeheerCaseTrackCreate',
              path: 'appointment/',
              beforeEnter: authGuard,
              components: {
                default: BeheerCaseDetail,
                modal: TrackCrud,
              },
              props: true,
            },
            {
              name: 'BeheerCaseTrackDetail',
              path: 'track/:trackId',
              beforeEnter: authGuard,
              components: {
                default: BeheerCaseDetail,
                modal: TrackCrud,
              },
              props: {
                default: true,
                modal: true,
              },
              children: [
                {
                  path: 'create-form/:formTemplateName',
                  name: 'BeheerTrackFormCreate',
                  components: {
                    default: BeheerCaseDetail,
                    nestedForm: DialogForm,
                  },
                  props: {
                    default: true,
                    nestedForm: true,
                  },
                },
                {
                  path: 'form-data/:formDataId',
                  name: 'BeheerTrackFormData',
                  components: {
                    default: BeheerCaseDetail,
                    nestedForm: DialogForm,
                  },
                  props: {
                    default: true,
                    nestedForm: true,
                  },
                },
              ],
            },
            {
              path: 'request/:requestId/form-data/:formDataId',
              name: 'BeheerRequestFormData',
              components: {
                default: BeheerCaseDetail,
                modal: DialogForm,
              },
              props: {
                default: true,
                modal: true,
              },
            },
          ],
        },
        {
          path: 'track/',
          beforeEnter: authGuard,
          children: [
            {
              path: '',
              name: 'BeheerTrackMany',
              component: () => import('@/pages/Beheer/BeheerTrackMany.vue'),
            },
            {
              name: 'BeheerTrackDetail',
              path: ':trackId',
              components: {
                modal: TrackCrud,
                default: () => import('@/pages/Beheer/BeheerTrackMany.vue'),
              },
              props: {
                default: true,
                modal: true,
              },
            },
          ],
        },
        {
          path: 'appointment',
          name: 'BeheerAppointmentMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerAppointmentMany.vue'),
        },
        {
          path: 'case-task',
          name: 'BeheerTaskMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerTaskMany.vue'),
        },
        {
          path: 'user',
          name: 'BeheerUserMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerUserMany.vue'),
        },
        {
          path: 'product',
          name: 'BeheerProductMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerProductMany.vue'),
        },
        {
          path: 'form-data/',
          children: [
            {
              path: '',
              name: 'BeheerFormMany',
              beforeEnter: authGuard,
              component: () => import('@/pages/Beheer/BeheerFormMany.vue'),
            },
            {
              path: ':formDataId',
              name: 'BeheerFormDetail',
              beforeEnter: authGuard,
              components: {
                modal: DialogForm,
                default: () => import('@/pages/Beheer/BeheerFormMany.vue'),
              },
              props: {
                default: true,
                modal: true,
              },
            },
          ],
        },

        {
          path: 'track/:trackId/partner-organization',
          name: 'BeheerTrackPartnerOrganization',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerTrackPartnerOrganization.vue'),
          props: true,
        },
        {
          path: '/partner-organization',
          name: 'BeheerPartnerOrganizationMany',
          beforeEnter: authGuard,
          component: () => import('@/pages/Beheer/BeheerPartnerOrganizationMany.vue'),
        },
      ],
    },
  ],
})

async function handleKeyCloakAuth(to: RouteLocationNormalizedGeneric) {
  const { getKeycloakClient } = useKeycloak()
  const keycloakClient = await getKeycloakClient()

  // Initialize Keycloak first
  const { handleLogin } = useKeycloak()

  if (!keycloakClient?.didInitialize) {
    await handleLogin(to.path)
    return
  }
}

async function authGuard(
  to: RouteLocationNormalizedGeneric,
  from: RouteLocationNormalizedLoadedGeneric,
  next: NavigationGuardNext,
) {
  const requireAuth = true
  if (requireAuth) await handleKeyCloakAuth(to)

  const { fetchMe } = useAuth()
  try {
    await fetchMe()
  } catch (error) {
    router.push({ name: 'Unauthorized' })
    console.error(error)
  }

  // remove keycloak session data from URL
  const newPath = to.fullPath
    .replace(/[&?]code=[^&$]*/, '')
    .replace(/[&?#]state=[^&$]*/, '')
    .replace(/[&?]session_state=[^&$]*/, '')
    .replace(/[&?]iss=[^&$]*/, '')

  to.fullPath = newPath

  next()
}

export default router
