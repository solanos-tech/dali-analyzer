import type { Frame, FrameSource } from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const buildUrl = (path: string) => {
  if (!API_BASE_URL) {
    return path
  }
  return `${API_BASE_URL}${path}`
}

export const fetchFrames = async (source: FrameSource): Promise<Frame[]> => {
  const response = await fetch(buildUrl(`/api/frames?source=${source}`))

  if (!response.ok) {
    throw new Error(`Failed to fetch frames: ${response.status}`)
  }

  const data = (await response.json()) as Frame[]
  return data
}
