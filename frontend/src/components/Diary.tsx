import { useState, type FormEvent } from 'react'
import type { DiaryEntry, RoadmapStep } from '../api/client'
import { today, useDiary } from '../context/useMyCourse'

/** "Today", "Yesterday", "3 days ago", then the date. Only used inside the diary. */
function whenWritten(on: string): string {
  const days = Math.round((new Date(`${today()}T00:00:00`).getTime() - new Date(`${on}T00:00:00`).getTime()) / 86_400_000)
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return new Date(`${on}T00:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

/** One line above the tabs, so the student knows where to continue. */
export function LastTime({ onOpen }: { onOpen: () => void }) {
  const { entries } = useDiary()
  const last = entries[0]
  if (!last) return null
  const text = last.next || last.did || last.learned
  return (
    <p className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-lg bg-pine-soft p-3 text-sm print:hidden">
      <span aria-hidden="true">📝</span>
      <span><strong>Last time ({whenWritten(last.on).toLowerCase()}){last.next ? ', you planned' : ''}:</strong> {text}</span>
      <button type="button" className="cursor-pointer font-semibold text-teal underline" onClick={onOpen}>Open my diary</button>
    </p>
  )
}

const EMPTY = { did: '', learned: '', next: '', step: '' }

function EntryForm({ steps, start, onSave, onCancel }: {
  steps: RoadmapStep[]
  start?: DiaryEntry
  onSave: (entry: { did: string; learned: string; next: string; step: number | null; on: string; id?: string }) => void
  onCancel?: () => void
}) {
  const [form, setForm] = useState(start
    ? { did: start.did, learned: start.learned, next: start.next, step: start.step ? String(start.step) : '' }
    : EMPTY)
  const empty = !form.did.trim() && !form.learned.trim() && !form.next.trim()
  const box = (key: 'did' | 'learned' | 'next', label: string, hint: string) => (
    <label className="block">
      <span className="mb-1 block text-sm font-semibold">{label}</span>
      <textarea
        className="input" rows={2} maxLength={500} placeholder={hint} value={form[key]}
        onChange={(event) => setForm({ ...form, [key]: event.target.value })}
      />
    </label>
  )

  function submit(event: FormEvent) {
    event.preventDefault()
    if (empty) return
    onSave({ ...form, step: form.step ? Number(form.step) : null, on: start?.on ?? today(), id: start?.id })
    if (!start) setForm(EMPTY)
  }

  return (
    <form onSubmit={submit} className="grid gap-3">
      {box('did', 'What I did', 'For example: watched 2 Python videos and wrote a calculator')}
      {box('learned', 'What I learned', 'For example: how loops work')}
      {box('next', "What I'll do next", 'For example: start the networking basics step')}
      <label className="block">
        <span className="mb-1 block text-sm font-semibold">Which step is this about? (optional)</span>
        <select className="input" value={form.step} onChange={(event) => setForm({ ...form, step: event.target.value })}>
          <option value="">Not about one step</option>
          {steps.map((step) => <option key={step.id} value={step.id}>Year {step.year}: {step.title}</option>)}
        </select>
      </label>
      <div className="flex flex-wrap gap-2">
        <button type="submit" className="btn btn-primary" disabled={empty}>{start ? 'Save changes' : 'Save entry'}</button>
        {onCancel && <button type="button" className="btn btn-outline" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  )
}

/** The My Diary tab: write what you did and learned, look back, and search. */
export function Diary({ steps }: { steps: RoadmapStep[] }) {
  const { entries, save, remove } = useDiary()
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState('')
  const [saved, setSaved] = useState(false)
  const stepName = (id?: number | null) => steps.find((step) => step.id === id)?.title
  const words = search.trim().toLowerCase()
  const shown = words
    ? entries.filter((entry) => [entry.did, entry.learned, entry.next, stepName(entry.step) ?? ''].join(' ').toLowerCase().includes(words))
    : entries

  return (
    <section className="mt-4">
      <div className="card print:hidden">
        <h2 className="text-xl">Write today's entry</h2>
        <p className="mb-3 mt-1 text-sm text-muted">Fill any box you like. Only you can see your diary.</p>
        <EntryForm steps={steps} onSave={(entry) => { save(entry); setSaved(true); window.setTimeout(() => setSaved(false), 2500) }} />
        {saved && <p className="mt-2 text-sm font-semibold text-teal" role="status">✓ Saved</p>}
      </div>

      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <h2 className="text-2xl">My diary ({entries.length})</h2>
        {entries.length > 0 && (
          <div className="flex flex-wrap gap-2 print:hidden">
            <label className="sr-only" htmlFor="diary-search">Search my diary</label>
            <input id="diary-search" className="input !w-56" placeholder="Search, for example SQL" value={search} onChange={(event) => setSearch(event.target.value)} />
            <button type="button" className="btn btn-outline" onClick={() => window.print()}>Print</button>
          </div>
        )}
      </div>

      {entries.length === 0 && <p className="mt-2 text-muted">No entries yet. Write your first one above. Even one line a day helps you remember.</p>}
      {entries.length > 0 && shown.length === 0 && <p className="mt-2 text-muted">Nothing matches "{search}".</p>}

      <ol className="mt-3 grid gap-3">
        {shown.map((entry) => (
          <li key={entry.id} className="card">
            {editing === entry.id ? (
              <EntryForm steps={steps} start={entry} onSave={(changed) => { save(changed); setEditing('') }} onCancel={() => setEditing('')} />
            ) : (
              <>
                <p className="text-sm font-semibold text-teal">
                  {whenWritten(entry.on)}{stepName(entry.step) ? ` · ${stepName(entry.step)}` : ''}
                </p>
                {entry.did && <p className="mt-1"><strong>Did:</strong> {entry.did}</p>}
                {entry.learned && <p className="mt-1"><strong>Learned:</strong> {entry.learned}</p>}
                {entry.next && <p className="mt-1"><strong>Next:</strong> {entry.next}</p>}
                <div className="mt-2 flex gap-3 text-sm print:hidden">
                  <button type="button" className="cursor-pointer text-teal underline" onClick={() => setEditing(entry.id)}>Edit</button>
                  <button
                    type="button" className="cursor-pointer text-muted underline"
                    onClick={() => { if (window.confirm('Delete this diary entry?')) remove(entry.id) }}
                  >
                    Delete
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ol>
    </section>
  )
}
