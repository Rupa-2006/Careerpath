import { useEffect, useState, type FormEvent } from 'react'
import { api, type ApiError, type PathChangeStatus, type RoadmapSummary } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Field, Notice } from './Form'

const STATUS_TEXT: Record<string, string> = {
  pending: '⏳ Waiting for an admin to answer',
  approved: '✅ Approved',
  rejected: '❌ Not approved',
}

/** On the Account page: change your career yourself. After the first change, once every 6 months. No admin needed. */
export function PathChange() {
  const { setUser } = useAuth()
  const [state, setState] = useState<PathChangeStatus | null>(null)
  const [careers, setCareers] = useState<RoadmapSummary[]>([])
  const [path, setPath] = useState('')
  const [reason, setReason] = useState('')
  const [sure, setSure] = useState(false)
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.pathChange().then(setState).catch((problem: ApiError) => setError(problem.message))
    api.roadmaps('en').then(setCareers).catch(() => setCareers([]))
  }, [])

  if (!state) return null
  const current = careers.find((item) => item.slug === state.path)?.name ?? state.path
  const free = state.free_left > 0
  const waiting = state.latest?.status === 'pending'
  const locked = state.next_change_on
    ? new Date(state.next_change_on).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })
    : ''

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const result = await api.changePath(path, reason)
      setMessage(result.message)
      setState(await api.pathChange())
      setUser(await api.me())   // a changed path shows everywhere at once
      setPath('')
      setReason('')
      setSure(false)
    } catch (problem) {
      setError((problem as ApiError).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card mb-4">
      <h2 className="text-xl">My career path</h2>
      <p className="mt-1">Your path: <strong>{current || 'not chosen'}</strong></p>
      <Notice kind="success">{message}</Notice>
      <Notice kind="error">{error}</Notice>

      {state.latest && (
        <div className="mt-3 rounded-lg bg-pine-soft p-3 text-sm">
          <p><strong>Your last request:</strong> {state.latest.from_name} → {state.latest.to_name}</p>
          <p className="mt-1">{STATUS_TEXT[state.latest.status] ?? state.latest.status}</p>
        </div>
      )}

      {locked && !waiting && (
        <p className="mt-3 text-sm text-muted">You can change your path again from <strong>{locked}</strong>. This keeps your path steady while you work on it.</p>
      )}
      {!waiting && !locked && (
        <form onSubmit={submit} className="mt-4">
          <p className="mb-3 text-sm text-muted">
            {free
              ? 'You can change your path yourself. Your progress is kept: if you ever come back to this path, your ticks return.'
              : 'You can change your path again now. After this, the next change is possible in 6 months.'}
          </p>
          <Field label="New career path">
            <select className="input" required value={path} onChange={(event) => setPath(event.target.value)}>
              <option value="">Choose a career</option>
              {careers.filter((item) => item.slug !== state.path).map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
            </select>
          </Field>
          <Field label="Why are you changing? (optional)">
            <textarea className="input" rows={2} maxLength={300} value={reason} onChange={(event) => setReason(event.target.value)} />
          </Field>
          {(
            <label className="mb-3 flex items-start gap-2 text-sm">
              <input type="checkbox" className="mt-1" checked={sure} onChange={(event) => setSure(event.target.checked)} />
              <span>I understand that after this change, I can change again only after <strong>6 months</strong>.</span>
            </label>
          )}
          <button type="submit" className="btn btn-primary" disabled={busy || !path || !sure}>
            {busy ? 'Please wait…' : 'Change my path'}
          </button>
        </form>
      )}
    </section>
  )
}

/** On the Admin page: students' requests to change their career. */
export function PathRequestsAdmin() {
  const [items, setItems] = useState<NonNullable<PathChangeStatus['latest']>[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.pathRequests().then(setItems).catch((problem: ApiError) => setError(problem.message))
  }, [])

  async function decide(id: number, approve: boolean) {
    try {
      await api.decidePathRequest(id, approve)
      setItems(await api.pathRequests())
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  const waiting = items.filter((item) => item.status === 'pending')
  const answered = items.filter((item) => item.status !== 'pending').slice(0, 5)

  return (
    <section className="mt-8">
      <h2 className="text-2xl">Path change requests ({waiting.length})</h2>
      <Notice kind="error">{error}</Notice>
      {waiting.length === 0 && <p className="mt-1 text-muted">No requests waiting.</p>}
      <ul className="mt-3 grid gap-3">
        {waiting.map((item) => (
          <li key={item.id} className="card">
            <p className="text-sm text-muted">{item.student_name || 'A student'} · {item.student_email} · {item.created_at.slice(0, 10)}</p>
            <p className="mt-1 font-semibold">{item.from_name} → {item.to_name}</p>
            <p className="mt-1"><strong>Reason:</strong> {item.reason}</p>
            <div className="mt-2 flex gap-2">
              <button type="button" className="btn btn-primary !min-h-9 !px-3 !py-1 text-sm" onClick={() => decide(item.id, true)}>Approve</button>
              <button type="button" className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm" onClick={() => decide(item.id, false)}>Reject</button>
            </div>
          </li>
        ))}
      </ul>
      {answered.length > 0 && (
        <details className="mt-3 text-sm">
          <summary className="cursor-pointer text-muted">Recently answered</summary>
          <ul className="mt-2 grid gap-1">
            {answered.map((item) => (
              <li key={item.id}>{item.student_email}: {item.from_name} → {item.to_name} · {STATUS_TEXT[item.status]}</li>
            ))}
          </ul>
        </details>
      )}
    </section>
  )
}
