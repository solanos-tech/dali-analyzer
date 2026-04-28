export type LegacyFrameSource = 'mock' | 'serial'

export type LegacyFrame = {
  timestamp: string
  address: string
  command: string
  source: LegacyFrameSource
}

export type FrameSource = 'simulated_log' | 'serial'

export type DecodeStatus = 'decoded' | 'reserved' | 'unknown' | 'ambiguous'

export type FrameDirection =
  | 'rx_forward16'
  | 'rx_forward24'
  | 'rx_backward'
  | 'tx_backward_local'
  | 'unknown'

export type RawFrame = {
  ts_ms: number
  direction: FrameDirection
  bit_length: number
  raw_hex: string
  source: FrameSource
  log_name: string | null
}

export type DecodedFrame = {
  frame_class: string
  name: string
  status: DecodeStatus
  addressing: string | null
  opcode: string | null
  params: Record<string, unknown>
  warnings: string[]
  confidence: number
}

export type TransactionInfo = {
  correlation_id: string | null
  expects_backward: boolean
  backward_raw_hex: string | null
  latency_ms: number | null
}

export type DecodedFrameRecord = {
  raw: RawFrame
  decoded: DecodedFrame
  transaction: TransactionInfo
}

export type LogFileInfo = {
  name: string
  path: string
  size_bytes: number
}

export type SerialPortInfo = {
  name: string
  description: string | null
}

export type SerialConnectionStatus = {
  connected: boolean
  port: string | null
  baudrate: number | null
  message: string | null
}
