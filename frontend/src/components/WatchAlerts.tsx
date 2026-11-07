import { useCallback, useEffect, useState } from 'react'
import { api, type ApiError, type SourceWatch } from '../api/client'
import { Notice } from './Form'

/** Official pages that changed. The site never updates itself: an admin reads the page, then changes the record. */
export function WatchAlerts() {
  const [items, setItems] = useState<SourceWatch[]>([])
  const [error, setError] = useState('')

  const load = useCallback(() => {
    api.watches().then(setItems).catch((problem: ApiError) => setError(problem.message))
  }, [])

  useEffect(load, [load])

  async function reviewed(id: number) {
    try {
      await api.watchReviewed(id)
      load()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  const changed = items.filter((item) => item.needs_review)
  const blocked = items.filter((item) => item.last_error)
  const lastRun = items.map((item) => item.last_checked_at).filter(Boolean).sort().at(-1)

  return (
    <section className="mt-8">
      <h2 className="text-2xl">Official page changes ({changed.length})</h2>
      <p className="mt-1 text-sm text-muted">
        Watching {items.length} pages. {lastRun ? `Last checked ${new Date(lastRun).toLocaleString('en-IN')}.` : 'Not checked yet.'} {blocked.length > 0 && `${blocked.length} could not be read.`}
      </p>
      <Notice kind="error">{error}</Notice>
      {changed.length === 0 && <p className="mt-2 text-muted">No changes to review.</p>}
      <ul className="mt-3 grid gap-3">
        {changed.map((item) => (
          <li key={item.id} className="card">
            <h3 className="text-lg">{item.name}</h3>
            <p className="text-sm"><strong>Affects:</strong> {item.affects}</p>
            {item.change_summary && <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded-lg bg-pine-soft p-2 text-sm">{item.change_summary}</pre>}
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="font-semibold">Open the official page ↗</a>
              <button type="button" className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm" onClick={() => void reviewed(item.id)}>Mark as reviewed</button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
