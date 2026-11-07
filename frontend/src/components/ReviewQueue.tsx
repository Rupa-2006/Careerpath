import { useCallback, useEffect, useState } from 'react'
import { api, type ApiError, type ReviewItem } from '../api/client'
import { Notice } from './Form'

const VIEWS = [
  ['pending_verification', 'Awaiting review'],
  ['verified', 'Checked'],
  ['published', 'Published'],
  ['outdated', 'Out of date'],
] as const

const GROUPS = [
  ['field', 'fields'],
  ['course', 'courses'],
  ['exam', 'exams'],
  ['criterion', 'eligibility rules'],
  ['roadmap', 'roadmaps'],
  ['date', 'dates'],
  ['skill', 'skills'],
  ['scholarship', 'scholarships'],
  ['listing', 'course list entries'],
  ['technology', 'technology changes'],
  ['opportunity', 'career opportunities'],
] as const

export function ReviewQueue({ onChange }: { onChange: () => void }) {
  const [view, setView] = useState<string>('pending_verification')
  const [items, setItems] = useState<ReviewItem[]>([])
  const [error, setError] = useState('')
  const [done, setDone] = useState('')
  const [group, setGroup] = useState('')
  const [checked, setChecked] = useState(false)

  const load = useCallback(async (status: string) => {
    try {
      setItems(await api.reviewQueue(status))
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }, [])

  useEffect(() => {
    api.reviewQueue(view).then(setItems).catch((problem: ApiError) => setError(problem.message))
    setGroup('')
    setChecked(false)
  }, [view])

  const canGroup = view === 'pending_verification' || view === 'verified'
  const ready = (entity: string) => items.filter((item) => item.entity === entity && item.source)
  const chosen = GROUPS.find(([entity]) => entity === group)
  const prechecked = items.filter((item) => item.prechecked && item.source)

  function openGroup(entity: string) {
    setGroup(entity === group ? '' : entity)
    setChecked(false)
    setDone('')
  }

  async function publishGroup(entity: string, label: string) {
    setError('')
    setDone('')
    try {
      const result = await api.publishGroup(entity, ready(entity).map((item) => item.id))
      setDone(`Published ${result.published} ${label}.${result.skipped ? ` ${result.skipped} could not be published.` : ''}`)
      setGroup('')
      setChecked(false)
      await load(view)
      onChange()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  async function publishPrechecked() {
    setError('')
    setDone('')
    let published = 0
    try {
      for (const [entity] of GROUPS) {
        const ids = prechecked.filter((item) => item.entity === entity).map((item) => item.id)
        if (ids.length > 0) published += (await api.publishGroup(entity, ids)).published
      }
      setDone(`Published ${published} pre-checked records.`)
      setGroup('')
      setChecked(false)
    } catch (problem) {
      setError(`${published} were published, then this failed: ${(problem as ApiError).message}`)
    }
    await load(view)
    onChange()
  }

  async function decide(item: ReviewItem, status: string) {
    setError('')
    try {
      await api.review(item.entity, item.id, status)
      await load(view)
      onChange()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  return (
    <section className="mt-8">
      <h2 className="text-2xl">Content review</h2>
      <p className="mt-1 max-w-2xl text-muted">Open the source, compare it with the text, then publish. Students only see published records.</p>
      <Notice kind="error">{error}</Notice>
      <Notice kind="success">{done}</Notice>
      <div className="my-3 flex flex-wrap gap-2">
        {VIEWS.map(([status, label]) => (
          <button key={status} type="button" onClick={() => setView(status)} className={`btn !min-h-9 !px-3 !py-1 text-sm ${view === status ? 'btn-primary' : 'btn-outline'}`}>{label}</button>
        ))}
      </div>
      {canGroup && items.length > 0 && (
        <div className="card mb-3">
          <h3 className="text-lg">Publish a whole group</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {prechecked.length > 0 && (
              <button type="button" aria-pressed={group === 'prechecked'} onClick={() => openGroup('prechecked')} className={`btn !min-h-9 !px-3 !py-1 text-sm ${group === 'prechecked' ? 'btn-primary' : 'btn-outline'}`}>
                {prechecked.length} pre-checked
              </button>
            )}
            {GROUPS.filter(([entity]) => ready(entity).length > 0).map(([entity, label]) => (
              <button key={entity} type="button" aria-pressed={group === entity} onClick={() => openGroup(entity)} className={`btn !min-h-9 !px-3 !py-1 text-sm ${group === entity ? 'btn-primary' : 'btn-outline'}`}>
                {ready(entity).length} {label}
              </button>
            ))}
          </div>
          {group === 'prechecked' && prechecked.length > 0 && (
            <div className="mt-3 rounded-lg bg-pine-soft p-3">
              <p className="text-sm">Only these {prechecked.length} records will be published. They matched official documents when Claude checked them, but Claude can make mistakes, so open a few sources yourself first. Students will see them straight away.</p>
              <label className="mt-2 flex items-start gap-2 text-sm font-semibold">
                <input type="checkbox" className="mt-1" checked={checked} onChange={(event) => setChecked(event.target.checked)} />
                I have looked at some of these myself, and I want to publish them.
              </label>
              <button type="button" disabled={!checked} className="btn btn-primary mt-2 !min-h-9 !px-3 !py-1 text-sm" onClick={() => void publishPrechecked()}>
                Publish {prechecked.length} pre-checked records
              </button>
            </div>
          )}
          {chosen && (
            <div className="mt-3 rounded-lg bg-pine-soft p-3">
              <p className="text-sm">Students will see all {ready(chosen[0]).length} {chosen[1]} straight away. Records with no source are left out.</p>
              <label className="mt-2 flex items-start gap-2 text-sm font-semibold">
                <input type="checkbox" className="mt-1" checked={checked} onChange={(event) => setChecked(event.target.checked)} />
                I have checked these {chosen[1]} against their official sources.
              </label>
              <button type="button" disabled={!checked} className="btn btn-primary mt-2 !min-h-9 !px-3 !py-1 text-sm" onClick={() => void publishGroup(chosen[0], chosen[1])}>
                Publish {ready(chosen[0]).length} {chosen[1]}
              </button>
            </div>
          )}
        </div>
      )}
      <ul className="grid gap-3">
        {items.map((item) => (
          <li key={`${item.entity}-${item.id}`} className="card">
            <p className="text-xs font-semibold uppercase text-muted">{item.entity}</p>
            <h3 className="text-lg">{item.title}</h3>
            <p className="mt-1 text-sm">{item.detail}</p>
            <p className="mt-1 text-sm">
              {item.source
                ? <a href={item.source.url} target="_blank" rel="noopener noreferrer">{item.source.name} ↗</a>
                : <span className="text-danger">No source. This can't be published.</span>}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {view !== 'published' && <button type="button" className="btn btn-primary !min-h-9 !px-3 !py-1 text-sm" onClick={() => decide(item, 'published')}>Publish</button>}
              {view !== 'verified' && view !== 'published' && <button type="button" className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm" onClick={() => decide(item, 'verified')}>Mark as checked</button>}
              {view !== 'outdated' && <button type="button" className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm" onClick={() => decide(item, 'outdated')}>Mark out of date</button>}
            </div>
          </li>
        ))}
        {items.length === 0 && <li className="text-muted">Nothing here.</li>}
      </ul>
    </section>
  )
}
