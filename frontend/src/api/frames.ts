import type {
  DecodedFrameRecord,
  FrameSource,
  LogFileInfo,
  SerialConnectionStatus,
  SerialPortInfo,
} from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const buildUrl = (path: string) => {
  if (!API_BASE_URL) {
    return path
  }
  return `${API_BASE_URL}${path}`
}

const buildQuery = (params: Record<string, string | number | undefined>) => {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      search.set(key, String(value))
    }
  })
  return search.toString()
}

export const fetchLogs = async (): Promise<LogFileInfo[]> => {
  const response = await fetch(buildUrl('/api/v2/logs'))
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch logs')
  }
  return (await response.json()) as LogFileInfo[]
}

export const fetchDecodedFrames = async (args: {
  source: FrameSource
  logName?: string
  limit?: number
}): Promise<DecodedFrameRecord[]> => {
  const query = buildQuery({
    source: args.source,
    log_name: args.logName,
    limit: args.limit ?? 100,
  })

  const response = await fetch(buildUrl(`/api/v2/frames?${query}`))
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch frames')
  }

  return (await response.json()) as DecodedFrameRecord[]
}

export const createStreamUrl = (args: { source: FrameSource; logName?: string }) => {
  const query = buildQuery({
    source: args.source,
    log_name: args.logName,
  })
  return buildUrl(`/api/v2/stream?${query}`)
}

export const fetchSerialPorts = async (): Promise<SerialPortInfo[]> => {
  const response = await fetch(buildUrl('/api/v2/serial/ports'))
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch serial ports')
  }
  return (await response.json()) as SerialPortInfo[]
}

export const fetchSerialStatus = async (): Promise<SerialConnectionStatus> => {
  const response = await fetch(buildUrl('/api/v2/serial/status'))
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to fetch serial status')
  }
  return (await response.json()) as SerialConnectionStatus
}

export const connectSerial = async (port: string): Promise<SerialConnectionStatus> => {
  const response = await fetch(buildUrl('/api/v2/serial/connect'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ port }),
  })
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to connect serial port')
  }
  return (await response.json()) as SerialConnectionStatus
}

export const disconnectSerial = async (): Promise<SerialConnectionStatus> => {
  const response = await fetch(buildUrl('/api/v2/serial/disconnect'), {
    method: 'POST',
  })
  if (!response.ok) {
    throw await buildApiError(response, 'Failed to disconnect serial port')
  }
  return (await response.json()) as SerialConnectionStatus
}

const buildApiError = async (response: Response, prefix: string): Promise<Error> => {
  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload?.detail) {
      return new Error(`${prefix}: ${payload.detail}`)
    }
  } catch {
    // ignore parse errors
  }
  return new Error(`${prefix}: ${response.status}`)
}
