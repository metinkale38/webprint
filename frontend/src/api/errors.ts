export function apiErrorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => (typeof entry === 'string' ? entry : entry?.msg))
      .filter((value): value is string => typeof value === 'string' && value.length > 0)
    if (messages.length > 0) {
      return messages.join(' ')
    }
  }
  return fallback
}
