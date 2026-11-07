import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type CourseListing } from '../api/client'
import { Notice } from '../components/Form'
import { TrustBadge } from '../components/Trust'

const STATES: Record<string, string> = { AP: 'Andhra Pradesh', TS: 'Telangana', India: 'All India' }

export function AllCourses() {
  const [items, setItems] = useState<CourseListing[]>([])
  const [query, setQuery] = useState('')
  const [state, setState] = useState('')
  const [group, setGroup] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.courseList().then(setItems).catch((problem: ApiError) => setError(problem.message))
  }, [])

  const groups = useMemo(() => [...new Set(items.map((item) => item.group_name))].sort(), [items])
  const words = query.trim().toLowerCase()
  const shown = items.filter((item) => (
    (!state || item.state === state || item.state === 'India')
    && (!group || item.group_name === group)
    && (!words || item.name.toLowerCase().includes(words))
  ))

  return (
    <>
      <h1 className="text-3xl">Full course list</h1>
      <p className="mt-3 max-w-3xl rounded-lg bg-pine-soft p-3">
        These course names come from official lists. Not every college offers every course, and this list is still growing.
      </p>
      <Notice kind="error">{error}</Notice>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <label className="font-semibold">
          Search
          <input className="input mt-1 w-full font-normal" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="For example, cyber security" />
        </label>
        <label className="font-semibold">
          State
          <select className="input mt-1 w-full font-normal" value={state} onChange={(event) => setState(event.target.value)}>
            <option value="">Both states</option>
            <option value="AP">Andhra Pradesh</option>
            <option value="TS">Telangana</option>
          </select>
        </label>
        <label className="font-semibold">
          Type of course
          <select className="input mt-1 w-full font-normal" value={group} onChange={(event) => setGroup(event.target.value)}>
            <option value="">All types</option>
            {groups.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>
        </label>
      </div>
      <p className="mt-4 text-muted" aria-live="polite">{shown.length} courses</p>
      <ul className="mt-2 grid gap-3 lg:grid-cols-2">
        {shown.map((item) => (
          <li key={`${item.name}-${item.state}`} className="card">
            <h2 className="text-base">{item.name}</h2>
            <p className="mt-1 text-sm">{item.group_name} · {STATES[item.state] ?? item.state} · {item.duration || 'Length not listed'}</p>
            <p className="text-sm">Admission route: {item.route}</p>
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <TrustBadge status={item.status} />
              {item.source && <a href={item.source.url} target="_blank" rel="noopener noreferrer" className="text-sm">{item.source.name} ↗</a>}
              {item.course_slug && <Link to={`/courses/${item.course_slug}`} className="text-sm font-semibold">More details →</Link>}
            </div>
          </li>
        ))}
      </ul>
    </>
  )
}
