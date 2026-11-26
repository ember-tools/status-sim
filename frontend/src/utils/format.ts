const relative = new Intl.RelativeTimeFormat('de', {numeric: 'auto'})

/**
 * How long ago something happened, in German words such as "vor 3 Minuten".
 *
 * @param timestamp the moment in seconds since the epoch
 * @returns the relative time
 */
export function formatRelativeTime(timestamp: number): string {
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - timestamp))
  if (seconds < 60) return relative.format(-seconds, 'second')
  if (seconds < 3600) return relative.format(-Math.round(seconds / 60), 'minute')
  if (seconds < 86400) return relative.format(-Math.round(seconds / 3600), 'hour')
  return relative.format(-Math.round(seconds / 86400), 'day')
}

/**
 * A duration as minutes and seconds, such as "03:07".
 *
 * @param seconds the duration in seconds
 * @returns the formatted duration
 */
export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  return `${String(minutes).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`
}
