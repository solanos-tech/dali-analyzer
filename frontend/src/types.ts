export type FrameSource = 'mock' | 'serial'

export type Frame = {
  timestamp: string
  address: string
  command: string
  source: FrameSource
}
