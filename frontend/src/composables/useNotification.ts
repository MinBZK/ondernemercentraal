import type { ToastMessageOptions } from 'primevue/toast'

type Severity = ToastMessageOptions['severity']

export type Notification = {
  message: string | string[]
  severity?: Severity
  life?: number | null
}

const notifications = ref<Notification[]>([])

export function useNotification() {
  function getToast(notification: Notification) {
    const severity = notification.severity || 'success'
    const life = severity == 'error' || notification.life === null ? undefined : 3000

    return {
      summary: notification.message,
      severity,
      life,
    }
  }

  function notify(notification: Notification) {
    notifications.value.push(notification)
  }

  return { notifications, getToast, notify }
}
