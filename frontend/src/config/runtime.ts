type RuntimeConfig = {
  apiBaseUrl?: string
}

let runtimeApiBaseUrl: string | null = null

const normalizeBaseUrl = (value: string) => value.trim().replace(/\/$/, '')

export const initializeRuntimeConfig = async (): Promise<void> => {
  try {
    const response = await fetch('/config/runtime-config.json', {
      cache: 'no-store',
    })
    if (!response.ok) {
      return
    }

    const payload = (await response.json()) as RuntimeConfig
    if (typeof payload.apiBaseUrl !== 'string') {
      return
    }

    const normalized = normalizeBaseUrl(payload.apiBaseUrl)
    runtimeApiBaseUrl = normalized.length > 0 ? normalized : null
  } catch {
    // Ignore runtime config errors and fall back to build-time settings.
  }
}

export const resolveApiBaseUrl = (): string => {
  if (runtimeApiBaseUrl) {
    return runtimeApiBaseUrl
  }
  return normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL ?? '')
}
