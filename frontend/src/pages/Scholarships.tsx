import { useEffect, useState } from 'react'
import { api, type ApiError, type Scholarship } from '../api/client'
import { Notice } from '../components/Form'
import { SourceLine, TrustBadge } from '../components/Trust'

const FILTERS = [
  ['all', 'All'],
  ['girls', 'For girls'],
  ['disability', 'For students with a disability'],
  ['loan', 'Education loans'],
  ['AP', 'Andhra Pradesh'],
  ['TS', 'Telangana'],
] as const

type Filter = (typeof FILTERS)[number][0]

function matches(item: Scholarship, filter: Filter) {
  if (filter === 'all') return true
  if (filter === 'loan') return item.kind === 'loan'
  if (filter === 'AP' || filter === 'TS') return item.state === filter
  return item.audience === filter
}

export function Scholarships() {
  const [items, setItems] = useState<Scholarship[]>([])
  const [filter, setFilter] = useState<Filter>('all')
  const [error, setError] = useState('')

  useEffect(() => {
    api.scholarships().then(setItems).catch((problem: ApiError) => setError(problem.message))
  }, [])

  const shown = items.filter((item) => matches(item, filter))

  return (
    <>
      <h1 className="text-3xl">Scholarships and loans</h1>
      <p className="mt-3 max-w-3xl rounded-lg bg-pine-soft p-3">
        Rules and amounts can change every year. Always confirm them on the official website before you apply.
      </p>
      <Notice kind="error">{error}</Notice>
      <div className="mt-4 flex flex-wrap gap-2" role="group" aria-label="Filter scholarships">
        {FILTERS.map(([value, label]) => (
          <button
            key={value} type="button" aria-pressed={filter === value} onClick={() => setFilter(value)}
            className={`cursor-pointer rounded-full border px-3 py-1 text-sm ${filter === value ? 'border-pine bg-pine text-white' : 'border-pine/40'}`}
          >
            {label}
          </button>
        ))}
      </div>
      {!error && items.length > 0 && shown.length === 0 && <p className="mt-4">Nothing here yet.</p>}
      <ul className="mt-4 grid gap-4 lg:grid-cols-2">
        {shown.map((item) => (
          <li key={item.slug} className="card">
            <h2 className="text-lg">{item.name}</h2>
            <p className="mt-1 text-sm">{item.run_by}</p>
            <div className="mt-2"><TrustBadge status={item.status} /></div>
            <h3 className="mt-3 font-semibold">Who can apply</h3>
            <p>{item.who_can_apply}</p>
            <h3 className="mt-3 font-semibold">What you get</h3>
            <p>{item.what_you_get}</p>
            <h3 className="mt-3 font-semibold">How to apply</h3>
            <p>{item.how_to_apply}</p>
            <a href={item.apply_url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block font-semibold">
              {new URL(item.apply_url).hostname.replace(/^www\./, '')} ↗
            </a>
            <SourceLine record={item} />
          </li>
        ))}
      </ul>
    </>
  )
}
