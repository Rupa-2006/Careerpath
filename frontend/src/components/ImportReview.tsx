import { useEffect, useState } from 'react'
import { api, type ApiError, type ImportBatch } from '../api/client'
import { Notice } from './Form'

export function ImportReview() {
  const [batches, setBatches] = useState<ImportBatch[]>([])
  const [error, setError] = useState('')
  const [needsOverride, setNeedsOverride] = useState(false)

  useEffect(() => {
    api.imports().then(setBatches).catch((problem: ApiError) => setError(problem.message))
  }, [])

  async function act(action: () => Promise<ImportBatch>) {
    setError('')
    try {
      await action()
      setNeedsOverride(false)
      setBatches(await api.imports())
    } catch (problem) {
      const failure = problem as ApiError
      setError(failure.message)
      setNeedsOverride(failure.status === 409 && failure.message.includes('unusually many'))
    }
  }

  const pending = batches.find((batch) => batch.status === 'pending')

  return (
    <section className="mt-8">
      <h2 className="text-2xl">College data imports</h2>
      <Notice kind="error">{error}</Notice>
      {!pending && (
        <p className="mt-1 max-w-2xl text-muted">
          Nothing is waiting. To load colleges, follow "Loading real colleges" in the README.
        </p>
      )}
      {pending && (
        <div className="card mt-3">
          <h3 className="text-lg">{pending.file_name}</h3>
          <p className="text-sm text-muted">Source: <a href={pending.source.url} target="_blank" rel="noopener noreferrer">{pending.source.name} ↗</a></p>
          <dl className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-5">
            {([
              ['New', pending.rows_new], ['Changed', pending.rows_changed], ['Unchanged', pending.rows_unchanged],
              ['Rejected', pending.rows_rejected], ['Missing', pending.rows_missing],
            ] as const).map(([label, value]) => (
              <div key={label} className="rounded-lg bg-paper p-2">
                <dt className="text-xs text-muted">{label}</dt>
                <dd className="text-xl font-bold text-pine">{value.toLocaleString('en-IN')}</dd>
              </div>
            ))}
          </dl>
          {pending.problems.length > 0 && (
            <details className="mt-3">
              <summary className="cursor-pointer font-semibold text-teal">Why rows were rejected (first {pending.problems.length})</summary>
              <ul className="mt-1 list-disc pl-5 text-sm">{pending.problems.map((problem) => <li key={problem}>{problem}</li>)}</ul>
            </details>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" className="btn btn-primary" onClick={() => act(() => api.publishImport(pending.id, false))}>Publish this import</button>
            {needsOverride && (
              <button type="button" className="btn btn-danger" onClick={() => act(() => api.publishImport(pending.id, true))}>The file is complete. Publish anyway</button>
            )}
            <button type="button" className="btn btn-outline" onClick={() => act(() => api.rejectImport(pending.id))}>Reject</button>
          </div>
        </div>
      )}
      {batches.some((batch) => batch.status !== 'pending') && (
        <ul className="mt-3 text-sm text-muted">
          {batches.filter((batch) => batch.status !== 'pending').map((batch) => (
            <li key={batch.id}>{batch.created_at.slice(0, 10)}: {batch.file_name} ({batch.status})</li>
          ))}
        </ul>
      )}
    </section>
  )
}
