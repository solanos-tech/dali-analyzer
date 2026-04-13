import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { fetchFrames } from './api/frames'
import type { Frame, FrameSource } from './types'

function App() {
  const [source, setSource] = useState<FrameSource>('mock')
  const [frames, setFrames] = useState<Frame[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLive, setIsLive] = useState(false)

  const sourceLabel = useMemo(() => (source === 'mock' ? 'Mock stream' : 'Serial stream'), [source])

  const loadFrames = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await fetchFrames(source)
      setFrames(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!isLive) {
      return undefined
    }

    void loadFrames()
    const timer = window.setInterval(() => {
      void loadFrames()
    }, 1000)

    return () => {
      window.clearInterval(timer)
    }
  }, [isLive, source])

  useEffect(() => {
    void loadFrames()
    // run once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>DALI Frames Monitor</h1>
        <p>Live frontend integration with backend API.</p>
      </header>

      <section className="toolbar" aria-label="Frames controls">
        <label className="field" htmlFor="source">
          Source
          <select
            id="source"
            value={source}
            onChange={(event) => setSource(event.target.value as FrameSource)}
          >
            <option value="mock">Mock</option>
            <option value="serial">Serial</option>
          </select>
        </label>

        <div className="actions">
          <button type="button" onClick={() => void loadFrames()} disabled={isLoading}>
            Load once
          </button>
          <button type="button" onClick={() => setIsLive(true)} disabled={isLive}>
            Start live
          </button>
          <button type="button" onClick={() => setIsLive(false)} disabled={!isLive}>
            Stop
          </button>
        </div>
      </section>

      <section className="status-panel" aria-live="polite">
        <strong>{sourceLabel}</strong>
        <span>{isLive ? 'Live polling: ON (1s)' : 'Live polling: OFF'}</span>
        {isLoading && <span className="loading">Loading frames...</span>}
        {error && <span className="error">{error}</span>}
      </section>

      <section className="table-panel" aria-label="Frames table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Address</th>
              <th>Command</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {frames.map((frame, index) => (
              <tr key={`${frame.timestamp}-${frame.address}-${index}`}>
                <td>{frame.timestamp}</td>
                <td>{frame.address}</td>
                <td>{frame.command}</td>
                <td>{frame.source}</td>
              </tr>
            ))}
            {!isLoading && frames.length === 0 && (
              <tr>
                <td colSpan={4} className="empty">
                  No frames to display.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </main>
  )
}

export default App
