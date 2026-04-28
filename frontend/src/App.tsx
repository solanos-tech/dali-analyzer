import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import { createStreamUrl, fetchDecodedFrames, fetchLogs } from './api/frames'
import type {
  DecodedFrameRecord,
  DecodeStatus,
  FrameDirection,
  FrameSource,
  LogFileInfo,
} from './types'

type FilterState = {
  direction: 'all' | FrameDirection
  status: 'all' | DecodeStatus
  query: string
}

const DEFAULT_LOG = 'sniffer_log_example.log'

const formatConfidence = (value: number) => `${Math.round(value * 100)}%`

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
  const [filters, setFilters] = useState<FilterState>({ direction: 'all', status: 'all', query: '' })
  const eventSourceRef = useRef<EventSource | null>(null)

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

  const stopLive = () => {
    eventSourceRef.current?.close()
    eventSourceRef.current = null
    setIsLive(false)
    setLiveMode('off')
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
        return next.slice(0, 500)
      })
      setSelectedIndex(0)
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
      if (filters.query.trim()) {
        const needle = filters.query.trim().toLowerCase()
        const haystack = `${frame.raw.raw_hex} ${frame.decoded.name} ${frame.decoded.opcode ?? ''} ${frame.decoded.addressing ?? ''}`.toLowerCase()
        if (!haystack.includes(needle)) {
          return false
        }
      }
      return true
    })
  }, [frames, filters])

  const selectedFrame = filteredFrames[selectedIndex] ?? null

  useEffect(() => {
    if (selectedIndex >= filteredFrames.length) {
      setSelectedIndex(0)
    }
  }, [filteredFrames.length, selectedIndex])

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <h1>DALI Decode Monitor</h1>
          <p>Backend-decoded frames with live stream, semantic status and transaction correlation.</p>
        </div>
        <div className="live-indicator">
          <span className={`dot ${isLive ? 'on' : 'off'}`} />
          <span>{isLive ? `Live: ${liveMode.toUpperCase()}` : 'Live: OFF'}</span>
        </div>
      </header>

      <section className="toolbar" aria-label="Frames controls">
        <label className="field" htmlFor="source">
          Source mode
          <select
            id="source"
            value={source}
            onChange={(event) => setSource(event.target.value as FrameSource)}
          >
            <option value="simulated_log">Simulated log</option>
            <option value="serial">Serial</option>
          </select>
        </label>

        {source === 'simulated_log' && (
          <label className="field" htmlFor="log-name">
            Log file
            <select
              id="log-name"
              value={selectedLog}
              onChange={(event) => setSelectedLog(event.target.value)}
            >
              {logs.map((log) => (
                <option key={log.name} value={log.name}>
                  {log.name}
                </option>
              ))}
            </select>
          </label>
        )}

        <div className="actions">
          <button type="button" onClick={() => void loadFrames()} disabled={isLoading}>
            Refresh snapshot
          </button>
          <button type="button" onClick={() => setIsLive(true)} disabled={isLive}>
            Start live
          </button>
          <button type="button" onClick={stopLive} disabled={!isLive}>
            Stop
          </button>
        </div>
      </section>

      <section className="filters" aria-label="Frames filters">
        <label className="field" htmlFor="filter-direction">
          Direction
          <select
            id="filter-direction"
            value={filters.direction}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                direction: event.target.value as FilterState['direction'],
              }))
            }
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
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                status: event.target.value as FilterState['status'],
              }))
            }
          >
            <option value="all">All statuses</option>
            <option value="decoded">decoded</option>
            <option value="reserved">reserved</option>
            <option value="unknown">unknown</option>
            <option value="ambiguous">ambiguous</option>
          </select>
        </label>

        <label className="field field-grow" htmlFor="filter-query">
          Search
          <input
            id="filter-query"
            type="text"
            value={filters.query}
            onChange={(event) => setFilters((current) => ({ ...current, query: event.target.value }))}
            placeholder="opcode, name, raw hex"
          />
        </label>
      </section>

      <section className="status-panel" aria-live="polite">
        <strong>{source === 'simulated_log' ? `Simulated: ${selectedLog}` : 'Serial source'}</strong>
        <span>Frames shown: {filteredFrames.length}</span>
        {isLoading && <span className="loading">Loading snapshot...</span>}
        {error && <span className="error">{error}</span>}
      </section>

      <section className="split-view" aria-label="Decoded frames view">
        <div className="table-panel">
          <table>
            <thead>
              <tr>
                <th>ts_ms</th>
                <th>Direction</th>
                <th>Raw</th>
                <th>Name</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredFrames.map((frame, index) => (
                <tr
                  key={`${frame.raw.ts_ms}-${frame.raw.raw_hex}-${index}`}
                  className={index === selectedIndex ? 'selected-row' : ''}
                  onClick={() => setSelectedIndex(index)}
                >
                  <td>{frame.raw.ts_ms}</td>
                  <td>
                    <span className={`badge badge-direction ${frame.raw.direction}`}>{frame.raw.direction}</span>
                  </td>
                  <td>
                    <code>{frame.raw.raw_hex}</code>
                  </td>
                  <td>{frame.decoded.name}</td>
                  <td>
                    <span className={`badge badge-status ${frame.decoded.status}`}>{frame.decoded.status}</span>
                  </td>
                </tr>
              ))}
              {!isLoading && filteredFrames.length === 0 && (
                <tr>
                  <td colSpan={5} className="empty">
                    No frames match current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <aside className="details-panel" aria-label="Frame details">
          {!selectedFrame && <p className="empty">Select a frame to inspect details.</p>}

          {selectedFrame && (
            <>
              <h2>Frame details</h2>
              <div className="detail-grid">
                <div>
                  <span className="detail-label">Frame class</span>
                  <strong>{selectedFrame.decoded.frame_class}</strong>
                </div>
                <div>
                  <span className="detail-label">Addressing</span>
                  <strong>{selectedFrame.decoded.addressing ?? 'n/a'}</strong>
                </div>
                <div>
                  <span className="detail-label">Opcode</span>
                  <strong>{selectedFrame.decoded.opcode ?? 'n/a'}</strong>
                </div>
                <div>
                  <span className="detail-label">Confidence</span>
                  <strong>{formatConfidence(selectedFrame.decoded.confidence)}</strong>
                </div>
                <div>
                  <span className="detail-label">Correlation ID</span>
                  <strong>{selectedFrame.transaction.correlation_id ?? 'n/a'}</strong>
                </div>
                <div>
                  <span className="detail-label">Latency</span>
                  <strong>
                    {selectedFrame.transaction.latency_ms !== null
                      ? `${selectedFrame.transaction.latency_ms} ms`
                      : 'n/a'}
                  </strong>
                </div>
              </div>

              <section className="json-block">
                <h3>Params</h3>
                <pre>{JSON.stringify(selectedFrame.decoded.params, null, 2)}</pre>
              </section>

              <section className="json-block">
                <h3>Warnings</h3>
                {selectedFrame.decoded.warnings.length === 0 ? (
                  <p className="muted">No warnings</p>
                ) : (
                  <ul>
                    {selectedFrame.decoded.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                )}
              </section>
            </>
          )}
        </aside>
      </section>
    </main>
  )
}

export default App