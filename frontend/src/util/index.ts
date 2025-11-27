const sortArrayByKey = <T>(array: T[], key: keyof T): T[] => [
  ...array.sort((a, b) => {
    let x = a[key] || ''
    let y = b[key] || ''
    x = typeof x == 'string' ? x.toLowerCase() : x
    y = typeof y == 'string' ? y.toLowerCase() : y
    const result = x < y ? -1 : x > y ? 1 : 0
    return result
  }),
]

function getFilename(xhr: XMLHttpRequest) {
  let filename: string = ''
  const disposition = xhr.getResponseHeader('Content-Disposition')
  if (disposition && disposition.indexOf('attachment') !== -1) {
    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
    const matches = filenameRegex.exec(disposition)
    if (matches != null && matches[1]) {
      filename = matches[1].replace(/['"]/g, '')
    }
  }
  return filename
}

function save(xhr: XMLHttpRequest) {
  const blob: Blob = xhr.response
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')

  const filename = getFilename(xhr)
  a.style.display = 'none'
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
}

async function downloadFile(url: string, token: string) {
  const xhr = new XMLHttpRequest()
  xhr.open('GET', url, true)
  xhr.setRequestHeader('Authorization', 'Bearer ' + token)
  xhr.responseType = 'blob'
  xhr.onload = function (this) {
    if (this.status == 200) {
      save(this)
    } else {
      throw new Error(this.responseText)
    }
  }
  xhr.send()
}

function getFormValues<T extends string>(stateObject: Record<T, FormFieldState | undefined>) {
  const keys = Object.keys(stateObject)
  return keys.reduce((formValues, key) => {
    //@ts-expect-error: no types needed here, low level function and will be validated in runtime
    formValues[key] = stateObject[key]?.value || null
    return formValues
  }, {}) as Record<keyof T, FormValue>
}

function joinStringsSemantic(arr: string[], linkingWord: 'en' | 'of', useQuotes: boolean = false) {
  if (arr.length === 0) {
    return ''
  }
  if (arr.length === 1) {
    return arr[0]
  }

  const applyQuotes = (v: string) => (useQuotes ? `'${v}'` : v)

  const lastItem = arr[arr.length - 1]
  const restOfItems = arr.slice(0, arr.length - 1).map((v) => {
    return applyQuotes(v)
  })
  return restOfItems.join(', ') + ` ${linkingWord} ` + applyQuotes(lastItem)
}

export { sortArrayByKey, downloadFile, getFormValues, joinStringsSemantic }
