// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 prudek
import { useEffect, useMemo, useRef, useState } from 'react'
import type { PointerEvent as ReactPointerEvent, ReactNode } from 'react'
import './App.css'
import {
  connectSerial,
  createStreamUrl,
  disconnectSerial,
  fetchDecodedFrames,
  fetchLogs,
  fetchSerialPorts,
  fetchSerialStatus,
  sendSerialCommand,
} from './api/frames'
import type {
  DecodedFrameRecord,
  DecodeStatus,
  FrameDirection,
  FrameSource,
  LogFileInfo,
  SemanticLevel,
  SerialConnectionStatus,
  SerialPortInfo,
} from './types'

type FilterState = {
  direction: 'all' | FrameDirection
  status: 'all' | DecodeStatus
  semanticLevel: 'all' | SemanticLevel
  query: string
  errorsOnly: boolean
  commandsOnly: boolean
}

type AnalyzerTab = 'frames' | 'timeline' | 'analytics'
type DetailsTab = 'summary' | 'params' | 'warnings' | 'raw'

type AnalyzerStats = {
  frameCount: number
  filteredCount: number
  errorCount: number
  decodeRateFps: number | null
  avgLatencyMs: number | null
  confidence: number | null
  forwardCount: number
  backwardCount: number
}

type TimelineTick = {
  key: string
  left: number
  kind: 'forward' | 'backward' | 'error'
  height: number
}

const DEFAULT_LOG = 'sniffer_log_example.log'
const APP_VERSION = __APP_VERSION__
const LIVE_FRAME_LIMIT = 500

const DISCONNECTED_STATUS: SerialConnectionStatus = {
  connected: false,
  port: null,
  baudrate: null,
  message: 'Disconnected',
}

const isForwardDirection = (direction: FrameDirection) =>
  direction === 'rx_forward16' || direction === 'rx_forward24'

const isBackwardDirection = (direction: FrameDirection) =>
  direction === 'rx_backward' || direction === 'tx_backward_local'

const isErrorFrame = (frame: DecodedFrameRecord) =>
  frame.decoded.status === 'unknown' ||
  frame.decoded.status === 'ambiguous' ||
  frame.decoded.warnings.length > 0

const formatConfidence = (value: number) => `${Math.round(value * 100)}%`

const formatRelativeTime = (deltaMs: number) => {
  const safeMs = Math.max(deltaMs, 0)
  const minutes = Math.floor(safeMs / 60000)
  const seconds = Math.floor((safeMs % 60000) / 1000)
  const milliseconds = safeMs % 1000
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(milliseconds).padStart(3, '0')}`
}

const formatMetric = (value: number | null, suffix = '') => {
  if (value === null || Number.isNaN(value)) {
    return 'n/a'
  }
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`
}

const formatLogTimestamp = () => {
  const iso = new Date().toISOString()
  return iso.slice(0, 23).replace('T', ' ')
}

const frameToLogLine = (frame: DecodedFrameRecord) =>
  `[${formatLogTimestamp()}] sniffer ts_ms=${frame.raw.ts_ms} dir=${frame.raw.direction} raw=${frame.raw.raw_hex}`

const getFrameAddress = (frame: DecodedFrameRecord) => {
  const value = frame.decoded.params.address
  return typeof value === 'string' || typeof value === 'number' ? String(value) : frame.decoded.addressing
}

const buildDecodedBreakdown = (frame: DecodedFrameRecord) => {
  const parts = [frame.decoded.frame_class, frame.decoded.name]
  if (frame.decoded.opcode) {
    parts.push(`opcode ${frame.decoded.opcode}`)
  }
  if (frame.decoded.semantic_reason) {
    parts.push(frame.decoded.semantic_reason)
  }
  return parts.filter(Boolean).join('. ')
}

const buildTimelineTicks = (frames: DecodedFrameRecord[]): TimelineTick[] => {
  if (frames.length === 0) {
    return []
  }

  const minTs = frames.reduce((value, frame) => Math.min(value, frame.raw.ts_ms), frames[0].raw.ts_ms)
  const maxTs = frames.reduce((value, frame) => Math.max(value, frame.raw.ts_ms), frames[0].raw.ts_ms)
  const span = Math.max(maxTs - minTs, 1)

  return frames.map((frame, index) => {
    const kind = isErrorFrame(frame)
      ? 'error'
      : isBackwardDirection(frame.raw.direction)
        ? 'backward'
        : 'forward'
    const height = kind === 'error' ? 22 : isForwardDirection(frame.raw.direction) ? 18 : 14
    return {
      key: `${frame.raw.ts_ms}-${frame.raw.raw_hex}-${index}`,
      left: ((frame.raw.ts_ms - minTs) / span) * 100,
      kind,
      height,
    }
  })
}

const calculateStats = (frames: DecodedFrameRecord[], filteredFrames: DecodedFrameRecord[]): AnalyzerStats => {
  const sortedFrames = [...frames].sort((a, b) => a.raw.ts_ms - b.raw.ts_ms)
  const first = sortedFrames[0]
  const last = sortedFrames.at(-1)
  const spanSeconds = first && last ? Math.max((last.raw.ts_ms - first.raw.ts_ms) / 1000, 0) : 0
  const latencyValues = filteredFrames
    .map((frame) => frame.transaction.latency_ms)
    .filter((value): value is number => value !== null)
  const confidenceValues = filteredFrames.map((frame) => frame.decoded.confidence)

  return {
    frameCount: frames.length,
    filteredCount: filteredFrames.length,
    errorCount: frames.filter(isErrorFrame).length,
    decodeRateFps: spanSeconds > 0 ? frames.length / spanSeconds : null,
    avgLatencyMs:
      latencyValues.length > 0
        ? latencyValues.reduce((total, value) => total + value, 0) / latencyValues.length
        : null,
    confidence:
      confidenceValues.length > 0
        ? confidenceValues.reduce((total, value) => total + value, 0) / confidenceValues.length
        : null,
    forwardCount: frames.filter((frame) => isForwardDirection(frame.raw.direction)).length,
    backwardCount: frames.filter((frame) => isBackwardDirection(frame.raw.direction)).length,
  }
}

function AnalyzerHeader({ isLive, liveMode }: { isLive: boolean; liveMode: 'sse' | 'polling' | 'off' }) {
  return (
    <header className="analyzer-header">
      <div className="brand-mark" aria-hidden="true">
        ~
      </div>
      <div className="brand-copy">
        <h1>DALI Protocol Analyzer</h1>
        <p>Live DALI / DALI-2 traffic analysis, decoding and correlation</p>
      </div>
      <div className="header-tools" aria-label="Application tools">
        <button className="icon-button" type="button" title="Help" aria-label="Help">
          ?
        </button>
        <button className="icon-button" type="button" title="Settings" aria-label="Settings">
          *
        </button>
        <div className="live-indicator">
          <span className={`dot ${isLive ? 'on' : 'off'}`} />
          <span>{isLive ? `Live: ${liveMode.toUpperCase()}` : 'Live: OFF'}</span>
        </div>
      </div>
    </header>
  )
}

function ConnectionToolbar({
  source,
  logs,
  selectedLog,
  serialPorts,
  selectedSerialPort,
  serialStatus,
  isConnectingSerial,
  isLoading,
  isLive,
  stats,
  onSourceChange,
  onLogChange,
  onSerialPortChange,
  onRefreshPorts,
  onConnectSerial,
  onDisconnectSerial,
  onLoadFrames,
  onStartLive,
  onStopLive,
}: {
  source: FrameSource
  logs: LogFileInfo[]
  selectedLog: string
  serialPorts: SerialPortInfo[]
  selectedSerialPort: string
  serialStatus: SerialConnectionStatus
  isConnectingSerial: boolean
  isLoading: boolean
  isLive: boolean
  stats: AnalyzerStats
  onSourceChange: (source: FrameSource) => void
  onLogChange: (logName: string) => void
  onSerialPortChange: (port: string) => void
  onRefreshPorts: () => void
  onConnectSerial: () => void
  onDisconnectSerial: () => void
  onLoadFrames: () => void
  onStartLive: () => void
  onStopLive: () => void
}) {
  return (
    <section className="connection-toolbar" aria-label="Connection and source controls">
      <label className="field field-compact" htmlFor="source">
        Source mode
        <select id="source" value={source} onChange={(event) => onSourceChange(event.target.value as FrameSource)}>
          <option value="simulated_log">Simulated log</option>
          <option value="serial">Serial</option>
        </select>
      </label>

      {source === 'simulated_log' && (
        <label className="field field-wide" htmlFor="log-name">
          Log file
          <select id="log-name" value={selectedLog} onChange={(event) => onLogChange(event.target.value)}>
            {logs.map((log) => (
              <option key={log.name} value={log.name}>
                {log.name}
              </option>
            ))}
          </select>
        </label>
      )}

      {source === 'serial' && (
        <>
          <label className="field field-wide" htmlFor="serial-port">
            Serial port
            <select
              id="serial-port"
              value={selectedSerialPort}
              onChange={(event) => onSerialPortChange(event.target.value)}
            >
              {serialPorts.length === 0 && <option value="">No ports available</option>}
              {serialPorts.map((port) => (
                <option key={port.name} value={port.name}>
                  {port.name}
                  {port.description ? ` - ${port.description}` : ''}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="button-secondary" onClick={onRefreshPorts} disabled={isConnectingSerial}>
            Refresh ports
          </button>
          <button
            type="button"
            onClick={onConnectSerial}
            disabled={isConnectingSerial || serialStatus.connected || !selectedSerialPort}
          >
            Connect
          </button>
          <button
            type="button"
            className="button-secondary"
            onClick={onDisconnectSerial}
            disabled={isConnectingSerial || !serialStatus.connected}
          >
            Disconnect
          </button>
        </>
      )}

      <div className="toolbar-spacer" />
      <button
        type="button"
        className="button-secondary"
        onClick={onLoadFrames}
        disabled={isLoading || (source === 'serial' && !serialStatus.connected)}
      >
        Snapshot
      </button>
      <button
        type="button"
        className="button-success"
        onClick={onStartLive}
        disabled={isLive || (source === 'serial' && !serialStatus.connected)}
      >
        Start live
      </button>
      <button type="button" className="button-danger" onClick={onStopLive} disabled={!isLive}>
        Stop
      </button>

      <div className="metric-strip" aria-label="Analyzer metrics">
        <span className={`status-chip ${serialStatus.connected ? 'connected' : ''}`}>
          {source === 'serial' && serialStatus.connected ? `Connected ${serialStatus.port ?? ''}` : 'Source ready'}
        </span>
        <span className="metric-chip">
          Frames <strong>{stats.frameCount.toLocaleString()}</strong>
        </span>
        <span className="metric-chip">
          Errors <strong>{stats.errorCount.toLocaleString()}</strong>
        </span>
        <span className="metric-chip">
          Decode rate <strong>{formatMetric(stats.decodeRateFps, ' f/s')}</strong>
        </span>
      </div>
    </section>
  )
}

function StickyFilterBar({
  filters,
  onFiltersChange,
}: {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
}) {
  return (
    <section className="filter-bar" aria-label="Frame filters">
      <label className="field" htmlFor="filter-direction">
        Direction
        <select
          id="filter-direction"
          value={filters.direction}
          onChange={(event) => onFiltersChange({ ...filters, direction: event.target.value as FilterState['direction'] })}
        >
          <option value="all">All directions</option>
          <option value="rx_forward16">rx_forward16</option>
          <option value="rx_forward24">rx_forward24</option>
          <option value="rx_backward">rx_backward</option>
          <option value="tx_backward_local">tx_backward_local</option>
          <option value="unknown">unknown</option>
        </select>
      </label>

      <label className="field" htmlFor="filter-status">
        Decode status
        <select
          id="filter-status"
          value={filters.status}
          onChange={(event) => onFiltersChange({ ...filters, status: event.target.value as FilterState['status'] })}
        >
          <option value="all">All statuses</option>
          <option value="decoded">decoded</option>
          <option value="decoded_generic">decoded_generic</option>
          <option value="reserved">reserved</option>
          <option value="unknown">unknown</option>
          <option value="ambiguous">ambiguous</option>
        </select>
      </label>

      <label className="field" htmlFor="filter-semantic-level">
        Semantic level
        <select
          id="filter-semantic-level"
          value={filters.semanticLevel}
          onChange={(event) =>
            onFiltersChange({ ...filters, semanticLevel: event.target.value as FilterState['semanticLevel'] })
          }
        >
          <option value="all">All levels</option>
          <option value="generic">generic</option>
          <option value="instance_aware">instance_aware</option>
          <option value="full">full</option>
        </select>
      </label>

      <label className="field field-search" htmlFor="filter-query">
        Search
        <input
          id="filter-query"
          type="search"
          value={filters.query}
          onChange={(event) => onFiltersChange({ ...filters, query: event.target.value })}
          placeholder="Search opcode, name, raw hex..."
        />
      </label>

      <button type="button" className="button-ghost" aria-expanded="false">
        Advanced
      </button>
      <button
        type="button"
        className={`toggle-button ${filters.errorsOnly ? 'active' : ''}`}
        aria-pressed={filters.errorsOnly}
        onClick={() => onFiltersChange({ ...filters, errorsOnly: !filters.errorsOnly })}
      >
        Errors only
      </button>
      <button
        type="button"
        className={`toggle-button ${filters.commandsOnly ? 'active' : ''}`}
        aria-pressed={filters.commandsOnly}
        onClick={() => onFiltersChange({ ...filters, commandsOnly: !filters.commandsOnly })}
      >
        Commands
      </button>
      <span className="pinned-note">Filters are pinned</span>
    </section>
  )
}

function AnalyzerTabs({ activeTab, onTabChange }: { activeTab: AnalyzerTab; onTabChange: (tab: AnalyzerTab) => void }) {
  return (
    <nav className="tabs" aria-label="Analyzer views">
      {(['frames', 'timeline', 'analytics'] as AnalyzerTab[]).map((tab) => (
        <button
          key={tab}
          type="button"
          className={activeTab === tab ? 'active' : ''}
          onClick={() => onTabChange(tab)}
        >
          {tab[0].toUpperCase()}
          {tab.slice(1)}
        </button>
      ))}
    </nav>
  )
}

function FrameLogTable({
  frames,
  selectedIndex,
  minVisibleTsMs,
  isLoading,
  onSelectFrame,
}: {
  frames: DecodedFrameRecord[]
  selectedIndex: number
  minVisibleTsMs: number | null
  isLoading: boolean
  onSelectFrame: (index: number) => void
}) {
  const tableScrollRef = useRef<HTMLDivElement | null>(null)
  const rowRefs = useRef<(HTMLTableRowElement | null)[]>([])
  const scrollFrameRef = useRef<number | null>(null)

  useEffect(() => {
    const row = rowRefs.current[selectedIndex]
    const container = tableScrollRef.current
    if (!row || !container) {
      return
    }

    const rowTop = row.offsetTop
    const rowBottom = rowTop + row.offsetHeight
    const visibleTop = container.scrollTop
    const visibleBottom = visibleTop + container.clientHeight

    if (rowTop < visibleTop || rowBottom > visibleBottom) {
      container.scrollTo({
        top: Math.max(rowTop - container.clientHeight / 2 + row.offsetHeight / 2, 0),
        behavior: 'smooth',
      })
    }
  }, [selectedIndex, frames])

  useEffect(() => {
    return () => {
      if (scrollFrameRef.current !== null) {
        window.cancelAnimationFrame(scrollFrameRef.current)
      }
    }
  }, [])

  const handleTableScroll = () => {
    if (scrollFrameRef.current !== null) {
      return
    }

    scrollFrameRef.current = window.requestAnimationFrame(() => {
      scrollFrameRef.current = null
      const container = tableScrollRef.current
      if (!container || frames.length === 0) {
        return
      }

      const viewportCenter = container.scrollTop + container.clientHeight / 2
      let nearestIndex = selectedIndex
      let nearestDistance = Number.POSITIVE_INFINITY

      rowRefs.current.forEach((row, index) => {
        if (!row) {
          return
        }

        const rowCenter = row.offsetTop + row.offsetHeight / 2
        const distance = Math.abs(rowCenter - viewportCenter)
        if (distance < nearestDistance) {
          nearestIndex = index
          nearestDistance = distance
        }
      })

      if (nearestIndex !== selectedIndex) {
        onSelectFrame(nearestIndex)
      }
    })
  }

  return (
    <div className="table-panel" ref={tableScrollRef} onScroll={handleTableScroll}>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>ts_ms</th>
            <th>Direction</th>
            <th>Raw</th>
            <th>Name</th>
            <th>Status</th>
            <th>Correlation ID</th>
            <th>Level</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {frames.map((frame, index) => (
            <tr
              key={`${frame.raw.ts_ms}-${frame.raw.raw_hex}-${index}`}
              ref={(element) => {
                rowRefs.current[index] = element
              }}
              className={index === selectedIndex ? 'selected-row' : ''}
              onClick={() => onSelectFrame(index)}
            >
              <td>{formatRelativeTime(frame.raw.ts_ms - (minVisibleTsMs ?? frame.raw.ts_ms))}</td>
              <td>{frame.raw.ts_ms}</td>
              <td>
                <span className={`badge badge-direction ${frame.raw.direction}`}>{frame.raw.direction}</span>
              </td>
              <td>
                <code>{frame.raw.raw_hex}</code>
              </td>
              <td className="name-cell" title={frame.decoded.name}>
                {frame.decoded.name}
              </td>
              <td>
                <span className={`badge badge-status ${frame.decoded.status}`}>{frame.decoded.status}</span>
              </td>
              <td>{frame.transaction.correlation_id ?? <span className="subtle">n/a</span>}</td>
              <td>
                <span className="badge badge-level">{frame.decoded.semantic_level}</span>
              </td>
              <td>
                {frame.transaction.latency_ms !== null ? (
                  `${frame.transaction.latency_ms} ms`
                ) : (
                  <span className="subtle">n/a</span>
                )}
              </td>
            </tr>
          ))}
          {!isLoading && frames.length === 0 && (
            <tr>
              <td colSpan={9} className="empty">
                No frames match current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

function FrameDetailsPanel({ frame }: { frame: DecodedFrameRecord | null }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [activeDetailsTab, setActiveDetailsTab] = useState<DetailsTab>('summary')
  const paramsJson = frame ? JSON.stringify(frame.decoded.params, null, 2) : '{}'

  const copyParams = async () => {
    if (!frame || !navigator.clipboard) {
      return
    }
    await navigator.clipboard.writeText(paramsJson)
  }

  return (
    <aside className={`details-panel ${isCollapsed ? 'collapsed' : ''}`} aria-label="Frame details">
      <div className="panel-title">
        <h2>Frame details</h2>
        <div className="panel-actions">
          <button type="button" className="icon-button" title="Pin panel" aria-label="Pin panel">
            ^
          </button>
          <button
            type="button"
            className="icon-button"
            title={isCollapsed ? 'Expand details' : 'Collapse details'}
            aria-label={isCollapsed ? 'Expand details' : 'Collapse details'}
            onClick={() => setIsCollapsed((value) => !value)}
          >
            {isCollapsed ? '+' : '-'}
          </button>
        </div>
      </div>

      {!frame && <p className="empty">Select a frame to inspect details.</p>}

      {frame && !isCollapsed && (
        <>
          <div className="selected-frame-summary">
            <span className={`badge badge-direction ${frame.raw.direction}`}>{frame.raw.direction}</span>
            <strong title={frame.decoded.name}>{frame.decoded.name}</strong>
            <code>{frame.raw.raw_hex}</code>
          </div>

          <div className="detail-grid compact">
            <DetailValue label="Frame class" value={frame.decoded.frame_class} />
            <DetailValue label="Opcode" value={frame.decoded.opcode} />
            <DetailValue label="Correlation ID" value={frame.transaction.correlation_id} />
            <DetailValue
              label="Latency"
              value={frame.transaction.latency_ms !== null ? `${frame.transaction.latency_ms} ms` : null}
            />
            <DetailValue label="Status" value={frame.decoded.status} />
            <DetailValue label="Confidence" value={formatConfidence(frame.decoded.confidence)} />
          </div>

          <nav className="details-tabs" aria-label="Frame detail sections">
            {(['summary', 'params', 'warnings', 'raw'] as DetailsTab[]).map((tab) => (
              <button
                key={tab}
                type="button"
                className={activeDetailsTab === tab ? 'active' : ''}
                onClick={() => setActiveDetailsTab(tab)}
              >
                {tab[0].toUpperCase()}
                {tab.slice(1)}
              </button>
            ))}
          </nav>

          {activeDetailsTab === 'summary' && (
            <div className="detail-grid secondary">
              <DetailValue label="Addressing" value={frame.decoded.addressing} />
              <DetailValue label="Semantic level" value={frame.decoded.semantic_level} />
              <DetailValue label="Semantic name" value={frame.decoded.semantic_name} />
              <DetailValue label="Bit length" value={`${frame.raw.bit_length}`} />
              <DetailValue label="Source" value={frame.raw.source} />
              <DetailValue label="Backward raw" value={frame.transaction.backward_raw_hex} />
            </div>
          )}

          {activeDetailsTab === 'params' && (
            <section className="json-block">
              <div className="section-heading">
                <h3>Params ({Object.keys(frame.decoded.params).length})</h3>
                <button
                  type="button"
                  className="icon-button light"
                  title="Copy params JSON"
                  aria-label="Copy params JSON"
                  onClick={copyParams}
                >
                  copy
                </button>
              </div>
              <pre>{paramsJson}</pre>
            </section>
          )}

          {activeDetailsTab === 'warnings' && (
            <section className="detail-section panel-section">
              <h3>Warnings ({frame.decoded.warnings.length})</h3>
              {frame.decoded.warnings.length === 0 ? (
                <p className="subtle">No warnings</p>
              ) : (
                <ul>
                  {frame.decoded.warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {activeDetailsTab === 'raw' && (
            <section className="json-block">
              <div className="section-heading">
                <h3>Raw frame JSON</h3>
              </div>
              <pre>{JSON.stringify(frame, null, 2)}</pre>
            </section>
          )}

          <details className="detail-section compact-breakdown">
            <summary>Decoded breakdown</summary>
            <p>{buildDecodedBreakdown(frame) || 'No decoded breakdown available.'}</p>
          </details>
        </>
      )}
    </aside>
  )
}

function DetailValue({ label, value }: { label: string; value: string | number | null | undefined }) {
  const isEmpty = value === null || value === undefined || value === ''
  return (
    <div>
      <span className="detail-label">{label}</span>
      <strong className={isEmpty ? 'subtle' : ''}>{isEmpty ? 'n/a' : value}</strong>
    </div>
  )
}

function BusActivityMiniTimeline({
  frames,
  stats,
  selectedIndex,
  onSelectFrame,
}: {
  frames: DecodedFrameRecord[]
  stats: AnalyzerStats
  selectedIndex: number
  onSelectFrame: (index: number) => void
}) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const trackRef = useRef<HTMLDivElement | null>(null)
  const ticks = useMemo(() => buildTimelineTicks(frames), [frames])
  const timelineBounds = useMemo(() => {
    if (frames.length === 0) {
      return null
    }
    const minTs = frames.reduce((value, frame) => Math.min(value, frame.raw.ts_ms), frames[0].raw.ts_ms)
    const maxTs = frames.reduce((value, frame) => Math.max(value, frame.raw.ts_ms), frames[0].raw.ts_ms)
    return { minTs, maxTs, span: Math.max(maxTs - minTs, 1) }
  }, [frames])
  const markerLeft =
    timelineBounds && frames[selectedIndex]
      ? ((frames[selectedIndex].raw.ts_ms - timelineBounds.minTs) / timelineBounds.span) * 100
      : 0

  const selectNearestFrame = (clientX: number) => {
    const track = trackRef.current
    if (!track || !timelineBounds || frames.length === 0) {
      return
    }

    const rect = track.getBoundingClientRect()
    const ratio = Math.min(Math.max((clientX - rect.left) / rect.width, 0), 1)
    const targetTs = timelineBounds.minTs + timelineBounds.span * ratio
    let nearestIndex = 0
    let nearestDistance = Math.abs(frames[0].raw.ts_ms - targetTs)

    frames.forEach((frame, index) => {
      const distance = Math.abs(frame.raw.ts_ms - targetTs)
      if (distance < nearestDistance) {
        nearestIndex = index
        nearestDistance = distance
      }
    })

    onSelectFrame(nearestIndex)
  }

  const handleTimelinePointer = (event: ReactPointerEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.currentTarget.setPointerCapture(event.pointerId)
    selectNearestFrame(event.clientX)
  }

  return (
    <section className={`mini-timeline ${isCollapsed ? 'collapsed' : ''}`} aria-label="Bus activity timeline">
      <div className="timeline-header">
        <div>
          <strong>Bus activity timeline</strong>
          <span className="live-pill">LIVE</span>
        </div>
        <div className="timeline-legend">
          <span className="legend-item forward">Forward (cmd)</span>
          <span className="legend-item backward">Backward (rsp)</span>
          <span className="legend-item error">Errors</span>
          <button
            type="button"
            className="icon-button"
            title={isCollapsed ? 'Expand timeline' : 'Collapse timeline'}
            aria-label={isCollapsed ? 'Expand timeline' : 'Collapse timeline'}
            onClick={() => setIsCollapsed((value) => !value)}
          >
            {isCollapsed ? '+' : '-'}
          </button>
        </div>
      </div>
      {!isCollapsed && (
        <>
          <div
            className="timeline-track"
            ref={trackRef}
            role="slider"
            aria-label="Timeline time marker"
            aria-valuemin={timelineBounds?.minTs ?? 0}
            aria-valuemax={timelineBounds?.maxTs ?? 0}
            aria-valuenow={frames[selectedIndex]?.raw.ts_ms ?? 0}
            tabIndex={0}
            onPointerDown={handleTimelinePointer}
            onPointerMove={(event) => {
              if (event.buttons === 1) {
                event.preventDefault()
                selectNearestFrame(event.clientX)
              }
            }}
            onKeyDown={(event) => {
              if (event.key === 'ArrowLeft') {
                event.preventDefault()
                onSelectFrame(Math.max(selectedIndex - 1, 0))
              }
              if (event.key === 'ArrowRight') {
                event.preventDefault()
                onSelectFrame(Math.min(selectedIndex + 1, frames.length - 1))
              }
            }}
          >
            {ticks.length === 0 && <span className="empty-inline">No activity</span>}
            {ticks.map((tick) => (
              <span
                key={tick.key}
                className={`timeline-tick ${tick.kind}`}
                style={{ left: `${tick.left}%`, height: `${tick.height}px` }}
              />
            ))}
            {frames.length > 0 && (
              <span
                className="timeline-marker"
                style={{ left: `${markerLeft}%` }}
                title={`Selected frame ts_ms=${frames[selectedIndex]?.raw.ts_ms ?? 0}`}
              >
                <span className="timeline-marker-handle" />
              </span>
            )}
          </div>
          <div className="timeline-axis">
            <span>Window</span>
            <span>{stats.filteredCount.toLocaleString()} visible frames</span>
            <span>Now</span>
          </div>
        </>
      )}
    </section>
  )
}

function TimelineView({
  frames,
  selectedFrame,
  stats,
}: {
  frames: DecodedFrameRecord[]
  selectedFrame: DecodedFrameRecord | null
  stats: AnalyzerStats
}) {
  const ticks = useMemo(() => buildTimelineTicks(frames), [frames])

  return (
    <section className="analytics-layout" aria-label="Timeline and analytics preview">
      <div className="analytics-main">
        <BusActivityMiniTimeline
          frames={frames}
          stats={stats}
          selectedIndex={0}
          onSelectFrame={() => undefined}
        />
        <div className="event-lanes">
          <h2>Decoded event lanes</h2>
          <div className="lane-grid">
            <span>Forward (cmd)</span>
            <div className="lane-raster">
              {ticks.filter((tick) => tick.kind === 'forward').map((tick) => (
                <span key={tick.key} style={{ left: `${tick.left}%` }} />
              ))}
            </div>
            <span>Backward (rsp)</span>
            <div className="lane-raster backward">
              {ticks.filter((tick) => tick.kind === 'backward').map((tick) => (
                <span key={tick.key} style={{ left: `${tick.left}%` }} />
              ))}
            </div>
            <span>Errors</span>
            <div className="lane-raster error">
              {ticks.filter((tick) => tick.kind === 'error').map((tick) => (
                <span key={tick.key} style={{ left: `${tick.left}%` }} />
              ))}
            </div>
          </div>
        </div>
      </div>
      <SelectedEventInspector frame={selectedFrame} />
    </section>
  )
}

function AnalyticsView({ frames, stats }: { frames: DecodedFrameRecord[]; stats: AnalyzerStats }) {
  const topOpcodes = useMemo(() => {
    const counts = new Map<string, number>()
    frames.forEach((frame) => {
      const key = frame.decoded.opcode ?? frame.decoded.name
      counts.set(key, (counts.get(key) ?? 0) + 1)
    })
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
  }, [frames])

  const topAddresses = useMemo(() => {
    const counts = new Map<string, number>()
    frames.forEach((frame) => {
      const address = getFrameAddress(frame)
      if (address) {
        counts.set(address, (counts.get(address) ?? 0) + 1)
      }
    })
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
  }, [frames])

  return (
    <section className="analytics-cards" aria-label="Protocol metrics">
      <MetricCard title="Overview">
        <dl>
          <dt>Frames</dt>
          <dd>{stats.frameCount.toLocaleString()}</dd>
          <dt>Frame rate</dt>
          <dd>{formatMetric(stats.decodeRateFps, ' f/s')}</dd>
          <dt>Errors</dt>
          <dd>{stats.errorCount.toLocaleString()}</dd>
          <dt>Avg latency</dt>
          <dd>{formatMetric(stats.avgLatencyMs, ' ms')}</dd>
        </dl>
      </MetricCard>
      <MetricCard title="Command vs response">
        <div className="ratio-ring" aria-label="Forward and backward ratio">
          <span>{stats.forwardCount}</span>
          <small>cmd</small>
        </div>
        <p>
          Forward {stats.forwardCount.toLocaleString()} / Backward {stats.backwardCount.toLocaleString()}
        </p>
      </MetricCard>
      <MetricCard title="Top opcodes">
        <RankedList rows={topOpcodes} total={Math.max(frames.length, 1)} />
      </MetricCard>
      <MetricCard title="Most active addresses">
        <RankedList rows={topAddresses} total={Math.max(frames.length, 1)} />
      </MetricCard>
    </section>
  )
}

function SelectedEventInspector({ frame }: { frame: DecodedFrameRecord | null }) {
  return (
    <aside className="event-inspector">
      <h2>Selected event</h2>
      {!frame && <p className="subtle">No event selected.</p>}
      {frame && (
        <dl>
          <dt>Time</dt>
          <dd>{frame.raw.ts_ms}</dd>
          <dt>Direction</dt>
          <dd>{frame.raw.direction}</dd>
          <dt>Name</dt>
          <dd>{frame.decoded.name}</dd>
          <dt>Opcode</dt>
          <dd>{frame.decoded.opcode ?? 'n/a'}</dd>
          <dt>Raw</dt>
          <dd>{frame.raw.raw_hex}</dd>
          <dt>Latency</dt>
          <dd>{frame.transaction.latency_ms !== null ? `${frame.transaction.latency_ms} ms` : 'n/a'}</dd>
        </dl>
      )}
    </aside>
  )
}

function MetricCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="metric-card">
      <h2>{title}</h2>
      {children}
    </article>
  )
}

function RankedList({ rows, total }: { rows: [string, number][]; total: number }) {
  if (rows.length === 0) {
    return <p className="subtle">No data yet.</p>
  }

  return (
    <ol className="ranked-list">
      {rows.map(([label, count]) => (
        <li key={label}>
          <span>{label}</span>
          <strong>{count.toLocaleString()}</strong>
          <meter min={0} max={100} value={(count / total) * 100} />
        </li>
      ))}
    </ol>
  )
}

function AnalyzerStatusFooter({
  source,
  selectedLog,
  serialStatus,
  liveMode,
  error,
  isLoading,
  framesLength,
  onClearLog,
  onSaveLog,
}: {
  source: FrameSource
  selectedLog: string
  serialStatus: SerialConnectionStatus
  liveMode: 'sse' | 'polling' | 'off'
  error: string | null
  isLoading: boolean
  framesLength: number
  onClearLog: () => void
  onSaveLog: () => void
}) {
  return (
    <footer className="status-footer" aria-live="polite">
      <span>DALI Protocol Analyzer v{APP_VERSION}</span>
      <span className="footer-source">
        Data source: {source === 'simulated_log' ? selectedLog : `Serial (${serialStatus.port ?? 'disconnected'})`}
      </span>
      <span>Stream: {liveMode.toUpperCase()}</span>
      {isLoading && <span className="loading">Loading snapshot...</span>}
      {error && <span className="error">{error}</span>}
      <div className="footer-actions">
        <button type="button" className="button-secondary" onClick={onClearLog} disabled={framesLength === 0}>
          Clear log
        </button>
        <button type="button" className="button-secondary" onClick={onSaveLog} disabled={framesLength === 0}>
          Save log
        </button>
      </div>
    </footer>
  )
}

function App() {
  const [source, setSource] = useState<FrameSource>('simulated_log')
  const [logs, setLogs] = useState<LogFileInfo[]>([])
  const [selectedLog, setSelectedLog] = useState(DEFAULT_LOG)
  const [frames, setFrames] = useState<DecodedFrameRecord[]>([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLive, setIsLive] = useState(false)
  const [liveMode, setLiveMode] = useState<'sse' | 'polling' | 'off'>('off')
  const [activeTab, setActiveTab] = useState<AnalyzerTab>('frames')
  const [filters, setFilters] = useState<FilterState>({
    direction: 'all',
    status: 'all',
    semanticLevel: 'all',
    query: '',
    errorsOnly: false,
    commandsOnly: false,
  })
  const [serialPorts, setSerialPorts] = useState<SerialPortInfo[]>([])
  const [selectedSerialPort, setSelectedSerialPort] = useState<string>('')
  const [serialStatus, setSerialStatus] = useState<SerialConnectionStatus>(DISCONNECTED_STATUS)
  const [isConnectingSerial, setIsConnectingSerial] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  const stopLive = () => {
    eventSourceRef.current?.close()
    eventSourceRef.current = null
    setIsLive(false)
    setLiveMode('off')
  }

  const loadLogs = async () => {
    try {
      const result = await fetchLogs()
      setLogs(result)
      if (result.length > 0 && !result.some((item) => item.name === selectedLog)) {
        setSelectedLog(result[0].name)
      }
    } catch {
      setLogs([])
    }
  }

  const loadFrames = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await fetchDecodedFrames({
        source,
        logName: source === 'simulated_log' ? selectedLog : undefined,
        limit: 200,
      })
      setFrames(result)
      setSelectedIndex(0)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const loadSerialControls = async () => {
    setError(null)
    try {
      const [ports, status] = await Promise.all([fetchSerialPorts(), fetchSerialStatus()])
      setSerialPorts(ports)
      setSerialStatus(status)

      const preferred = status.port ?? ports[0]?.name ?? ''
      setSelectedSerialPort(preferred)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      setSerialPorts([])
      setSerialStatus(DISCONNECTED_STATUS)
      setSelectedSerialPort('')
    }
  }

  const startSseStream = () => {
    const url = createStreamUrl({
      source,
      logName: source === 'simulated_log' ? selectedLog : undefined,
    })

    const sourceHandle = new EventSource(url)
    eventSourceRef.current = sourceHandle
    setLiveMode('sse')

    sourceHandle.addEventListener('frame', (event) => {
      setError(null)
      const payload = JSON.parse((event as MessageEvent).data) as DecodedFrameRecord
      setFrames((previous) => {
        const next = [payload, ...previous]
        return next.slice(0, LIVE_FRAME_LIMIT)
      })
      setSelectedIndex(0)
    })

    sourceHandle.addEventListener('error', (event) => {
      if ((event as MessageEvent).data) {
        try {
          const payload = JSON.parse((event as MessageEvent).data) as { detail?: string }
          setError(payload.detail ?? 'Live stream error')
        } catch {
          setError('Live stream error')
        }
      }
    })

    sourceHandle.onerror = () => {
      sourceHandle.close()
      eventSourceRef.current = null
      setLiveMode('polling')
    }
  }

  useEffect(() => {
    void loadLogs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (source === 'serial') {
      void loadSerialControls()
      setFrames([])
      setSelectedIndex(0)
      stopLive()
      return
    }
    void loadFrames()
    stopLive()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source, selectedLog])

  useEffect(() => {
    if (!isLive) {
      return undefined
    }

    startSseStream()

    return () => {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLive, source, selectedLog])

  useEffect(() => {
    if (!isLive || liveMode !== 'polling') {
      return undefined
    }

    const timer = window.setInterval(() => {
      void loadFrames()
    }, 1000)

    return () => {
      window.clearInterval(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLive, liveMode, source, selectedLog])

  const filteredFrames = useMemo(() => {
    return frames.filter((frame) => {
      if (filters.direction !== 'all' && frame.raw.direction !== filters.direction) {
        return false
      }
      if (filters.status !== 'all' && frame.decoded.status !== filters.status) {
        return false
      }
      if (filters.semanticLevel !== 'all' && frame.decoded.semantic_level !== filters.semanticLevel) {
        return false
      }
      if (filters.errorsOnly && !isErrorFrame(frame)) {
        return false
      }
      if (filters.commandsOnly && !isForwardDirection(frame.raw.direction)) {
        return false
      }
      if (filters.query.trim()) {
        const needle = filters.query.trim().toLowerCase()
        const haystack =
          `${frame.raw.raw_hex} ${frame.decoded.name} ${frame.decoded.opcode ?? ''} ${frame.decoded.addressing ?? ''} ${frame.decoded.semantic_name ?? ''} ${frame.transaction.correlation_id ?? ''}`.toLowerCase()
        if (!haystack.includes(needle)) {
          return false
        }
      }
      return true
    })
  }, [frames, filters])

  const minVisibleTsMs = useMemo(() => {
    if (filteredFrames.length === 0) {
      return null
    }
    return filteredFrames.reduce((minTs, frame) => Math.min(minTs, frame.raw.ts_ms), filteredFrames[0].raw.ts_ms)
  }, [filteredFrames])

  const selectedFrame = filteredFrames[selectedIndex] ?? null
  const stats = useMemo(() => calculateStats(frames, filteredFrames), [frames, filteredFrames])

  useEffect(() => {
    if (selectedIndex >= filteredFrames.length) {
      setSelectedIndex(0)
    }
  }, [filteredFrames.length, selectedIndex])

  const handleConnectSerial = async () => {
    if (!selectedSerialPort) {
      setError('Choose a serial port first')
      return
    }
    setIsConnectingSerial(true)
    setError(null)
    try {
      const status = await connectSerial(selectedSerialPort)
      setSerialStatus(status)
      await loadFrames()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
    } finally {
      setIsConnectingSerial(false)
    }
  }

  const handleDisconnectSerial = async () => {
    setIsConnectingSerial(true)
    setError(null)
    try {
      const status = await disconnectSerial()
      setSerialStatus(status)
      stopLive()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
    } finally {
      setIsConnectingSerial(false)
    }
  }

  const handleClearLog = () => {
    setFrames([])
    setSelectedIndex(0)
    setError(null)
  }

  const handleSaveLog = () => {
    if (frames.length === 0) {
      setError('No frames to save')
      return
    }

    const lines = frames.map(frameToLogLine).join('\n')
    const blob = new Blob([lines], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const stamp = new Date().toISOString().replaceAll(':', '').replaceAll('-', '').replace('T', '-').slice(0, 15)
    const filename = `dali-sniffer-${stamp}.log`
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  const handleStartLive = async () => {
    if (source === 'serial' && !serialStatus.connected) {
      setError('Connect a serial port before starting live stream')
      return
    }

    setError(null)
    if (source === 'serial') {
      try {
        await sendSerialCommand('sniffer_on')
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        setError(message)
        return
      }
    }
    setIsLive(true)
  }

  return (
    <main className="app-shell">
      <AnalyzerHeader isLive={isLive} liveMode={liveMode} />
      <ConnectionToolbar
        source={source}
        logs={logs}
        selectedLog={selectedLog}
        serialPorts={serialPorts}
        selectedSerialPort={selectedSerialPort}
        serialStatus={serialStatus}
        isConnectingSerial={isConnectingSerial}
        isLoading={isLoading}
        isLive={isLive}
        stats={stats}
        onSourceChange={setSource}
        onLogChange={setSelectedLog}
        onSerialPortChange={setSelectedSerialPort}
        onRefreshPorts={() => void loadSerialControls()}
        onConnectSerial={() => void handleConnectSerial()}
        onDisconnectSerial={() => void handleDisconnectSerial()}
        onLoadFrames={() => void loadFrames()}
        onStartLive={() => void handleStartLive()}
        onStopLive={stopLive}
      />
      <StickyFilterBar filters={filters} onFiltersChange={setFilters} />
      <AnalyzerTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'frames' && (
        <>
          <BusActivityMiniTimeline
            frames={filteredFrames}
            stats={stats}
            selectedIndex={selectedIndex}
            onSelectFrame={setSelectedIndex}
          />
          <section className="split-view" aria-label="Decoded frames view">
            <FrameLogTable
              frames={filteredFrames}
              selectedIndex={selectedIndex}
              minVisibleTsMs={minVisibleTsMs}
              isLoading={isLoading}
              onSelectFrame={setSelectedIndex}
            />
            <FrameDetailsPanel frame={selectedFrame} />
          </section>
        </>
      )}

      {activeTab === 'timeline' && (
        <TimelineView frames={filteredFrames} selectedFrame={selectedFrame} stats={stats} />
      )}

      {activeTab === 'analytics' && <AnalyticsView frames={filteredFrames} stats={stats} />}

      <AnalyzerStatusFooter
        source={source}
        selectedLog={selectedLog}
        serialStatus={serialStatus}
        liveMode={liveMode}
        error={error}
        isLoading={isLoading}
        framesLength={frames.length}
        onClearLog={handleClearLog}
        onSaveLog={handleSaveLog}
      />
    </main>
  )
}

export default App
