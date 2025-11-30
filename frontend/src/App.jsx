import { useState, useEffect } from 'react'
import { fetchBackendStatus } from './api'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [backendStatus, setBackendStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const loadStatus = async (opts = {}) => {
    setLoading(true)
    setError(null)
    setBackendStatus(null)
    const controller = new AbortController()
    try {
      const data = await fetchBackendStatus({ signal: controller.signal, timeout: opts.timeout || 5000 })
      setBackendStatus(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
    return () => controller.abort()
  }

  useEffect(() => {
    loadStatus()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <>
      <header className="app-header">
        <h1>Auto-Ops-AI</h1>
        <p className="tagline">AI-powered IT Operations and Support — Frontend</p>
      </header>
      <div className="status-card">
        <div className="status-card-row">
          <strong>Backend status:</strong>
          <div className={`status-badge ${loading ? 'loading' : error ? 'error' : 'ok'}`}>
            {loading ? 'Loading...' : error ? 'Failed to fetch' : 'OK'}
          </div>
        </div>
        <div className="status-card-body">
          {error && <div className="status-error">{error}</div>}
          {backendStatus && <pre className="status-json">{JSON.stringify(backendStatus, null, 2)}</pre>}
        </div>
        <div className="status-actions">
          <button onClick={() => loadStatus()} className="btn">Retry</button>
        </div>
      </div>
      <main className="main-card">
        <div className="card">
          <h2>Quick links</h2>
          <ul>
            <li><a href="/docs" target="_blank">Backend API Docs</a></li>
            <li><a href="/api/v1/tickets" target="_blank">Tickets API</a></li>
          </ul>
          <p>Local dev: edit <code>src/App.jsx</code> and save to test HMR.</p>
        </div>
      </main>
      <footer className="read-the-docs">
        <small>Backend base URL: <code>{import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'}</code></small>
      </footer>
    </>
  )
}

export default App
