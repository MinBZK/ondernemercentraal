type ConfirmationQuery = {
  question: string | string[]
  title: string
  requireUserMessage?: boolean
  isMessageRequired?: boolean
  warningMessage?: string
}

type ConfirmationResponse = {
  message: string
  confirmed: boolean
}

type ConfirmPromise = (response: ConfirmationResponse) => void

const confirmationQuery = ref<ConfirmationQuery>()
let resolveQuery: ConfirmPromise | null = null

export function useConfirm() {
  function askToConfirm(query: ConfirmationQuery) {
    confirmationQuery.value = query
    return new Promise<ConfirmationResponse>((resolve) => {
      resolveQuery = resolve
    })
  }

  function confirm(message: string) {
    if (resolveQuery) {
      resolveQuery({ message, confirmed: true })
      confirmationQuery.value = undefined
    } else {
      console.error('Confirmed without resolve query')
    }
  }

  function cancel() {
    if (resolveQuery) {
      confirmationQuery.value = undefined
    }
  }

  return { confirmationQuery, askToConfirm, confirm, cancel }
}
