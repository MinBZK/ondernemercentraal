import { format, formatDistanceToNowStrict } from 'date-fns'
import { nl } from 'date-fns/locale'

type DateFormatType = 'short' | 'long' | 'longDate' | 'time'

function getUtcDateFromString(date: string) {
  const dateFromString = new Date(date)
  const d = new Date(dateFromString.valueOf())
  return d
}

function formatDateOrTimeLike(value: string, dataType: DataTypeDateLike) {
  const dataTypeFormatMapping: Record<DataTypeDateLike, DateFormatType> = {
    date: 'short',
    'date-long': 'longDate',
    datetime: 'long',
    'relative-datetime': 'long',
    time: 'time',
  }

  if (dataType == 'relative-datetime') {
    return formatUtcDateRelative(value)
  } else {
    return formatUtcDate(value, dataTypeFormatMapping[dataType])
  }
}

function formatUtcDate(date: string, dateFormat: DateFormatType) {
  const dateFormats: Record<DateFormatType, string> = {
    long: 'iiii d LLLL yyyy HH:mm',
    longDate: 'iiii d LLLL yyyy',
    short: 'd LLLL yyyy',
    time: 'HH:mm',
  }
  return format(getUtcDateFromString(date), dateFormats[dateFormat], {
    locale: nl,
  })
}

function formatUtcDateRelative(date: string) {
  return formatDistanceToNowStrict(getUtcDateFromString(date), {
    addSuffix: true,
    locale: nl,
  })
}

function formatTimeSlot(start: string, end: string) {
  return `${formatUtcDate(start, 'longDate')} (${formatUtcDate(start, 'time')}-${formatUtcDate(end, 'time')})`
}

export { formatUtcDate, formatUtcDateRelative, formatTimeSlot, formatDateOrTimeLike }
