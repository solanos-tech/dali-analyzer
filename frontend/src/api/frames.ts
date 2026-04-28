import type { DecodedFrameRecord, FrameSource, LogFileInfo } from '../types'

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
    throw new Error(`Failed to fetch logs: ${response.status}`)
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
    throw new Error(`Failed to fetch frames: ${response.status}`)
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