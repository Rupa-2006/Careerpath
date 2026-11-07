import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CollegeFilters, type CollegeSummary, type Region } from '../api/client'
import { CollegeAttribution } from '../components/CollegeAttribution'
import { Field, Notice } from '../components/Form'
import { useAuth } from '../context/AuthContext'

export function Colleges() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [regions, setRegions] = useState<Region[]>([])
  const [filters, setFilters] = useState<CollegeFilters>({ districts: [], college_types: [], managements: [] })
  const [result, setResult] = useState<{ total: number; pages: number; colleges: CollegeSummary[] } | null>(null)
  const [text, setText] = useState(params.get('q') ?? '')
  const [chosen, setChosen] = useState<number[]>([])
  const [error, setError] = useState('')

  const region = params.get('region') ?? (user?.region_id ? String(user.region_id) : '')
  const page = Number(params.get('page') ?? '1')
  const course = params.get('course') ?? ''

  useEffect(() => {
    api.states().then(setRegions).catch(() => setRegions([]))
  }, [])

  useEffect(() => {
    api.collegeFilters(region ? Number(region) : null).then(setFilters).catch(() => undefined)
  }, [region])

  useEffect(() => {
    const query = new URLSearchParams(params)
    if (region) query.set('region', region)
    api.colleges(query.toString()).then(setResult).catch((problem: ApiError) => setError(problem.message))
  }, [params, region])

  function setParam(name: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(name, value)
    else next.delete(name)
    if (name !== 'page') next.delete('page')
    if (name === 'region') next.delete('district')
    setParams(next, { replace: true })
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    setParam('q', text.trim())
  }

  function toggle(id: number) {
    setChosen((items) => {
      if (items.includes(id)) return items.filter((item) => item !== id)
      return items.length < 3 ? [...items, id] : items
    })
  }

  const noData = result?.total === 0 && !region && !params.get('q') && !course

  return (
    <>
      <h1 className="text-3xl">Colleges</h1>
      <p className="mb-4 mt-2 max-w-2xl text-muted">Every college here comes from the Ministry of Education's official directory.</p>

      <div className="card grid gap-x-4 md:grid-cols-2 lg:grid-cols-4">
        <form onSubmit={submit} className="md:col-span-2 lg:col-span-4">
          <Field label="Search by college name">
            <span className="flex gap-2">
              <input className="input" type="search" maxLength={100} value={text} onChange={(event) => setText(event.target.value)} />
              <button type="submit" className="btn btn-primary">Search</button>
            </span>
          </Field>
        </form>
        <Field label="State or Union Territory">
          <select className="input" value={region} onChange={(event) => setParam('region', event.target.value)}>
            <option value="">All of India</option>
            {regions.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </Field>
        <Field label="District">
          <select className="input" disabled={!region} value={params.get('district') ?? ''} onChange={(event) => setParam('district', event.target.value)}>
            <option value="">{region ? 'All districts' : 'Choose a State first'}</option>
            {filters.districts.map((item) => <option key={item}>{item}</option>)}
          </select>
        </Field>
        <Field label="College type">
          <select className="input" value={params.get('college_type') ?? ''} onChange={(event) => setParam('college_type', event.target.value)}>
            <option value="">All types</option>
            {filters.college_types.map((item) => <option key={item}>{item}</option>)}
          </select>
        </Field>
        <Field label="Management">
          <select className="input" value={params.get('management') ?? ''} onChange={(event) => setParam('management', event.target.value)}>
            <option value="">All</option>
            {filters.managements.map((item) => <option key={item}>{item}</option>)}
          </select>
        </Field>
      </div>

      <Notice kind="error">{error}</Notice>
      {course && (
        <p className="mt-4 rounded-lg bg-pine-soft p-3">
          Showing colleges with a confirmed record of this course. The official directory doesn't list courses, so many colleges that offer it won't appear yet.{' '}
          <button type="button" className="cursor-pointer font-semibold text-teal underline" onClick={() => setParam('course', '')}>Show all colleges</button>
        </p>
      )}
      {noData && <p className="mt-6 text-muted">The official college list hasn't been published here yet.</p>}
      {result && !noData && <p className="mt-4 font-semibold">{result.total.toLocaleString('en-IN')} {result.total === 1 ? 'college' : 'colleges'}</p>}
      {result?.total === 0 && !noData && <p className="mt-2 text-muted">No colleges match. Try fewer filters.</p>}

      <ul className="mt-3 grid gap-3 pb-4 md:grid-cols-2">
        {result?.colleges.map((college) => (
          <li key={college.id} className="card">
            <h2 className="text-lg"><Link to={`/colleges/${college.id}`} className="text-pine">{college.name}</Link></h2>
            <p className="mt-1 text-sm text-muted">{[college.district, college.region.name].filter(Boolean).join(', ')}</p>
            <p className="mt-1 text-sm">{[college.college_type, college.management].filter(Boolean).join(' · ')}</p>
            {college.university_name && <p className="mt-1 text-sm text-muted">{college.university_name}</p>}
            <label className="mt-2 flex min-h-9 items-center gap-2 text-sm font-semibold text-teal">
              <input type="checkbox" checked={chosen.includes(college.id)} onChange={() => toggle(college.id)} /> Compare
            </label>
          </li>
        ))}
      </ul>

      {result && result.pages > 1 && (
        <nav aria-label="Pages" className="flex items-center justify-center gap-3 pb-20">
          <button type="button" className="btn btn-outline" disabled={page <= 1} onClick={() => setParam('page', String(page - 1))}>Previous</button>
          <span>Page {page} of {result.pages.toLocaleString('en-IN')}</span>
          <button type="button" className="btn btn-outline" disabled={page >= result.pages} onClick={() => setParam('page', String(page + 1))}>Next</button>
        </nav>
      )}

      <CollegeAttribution />

      {chosen.length > 0 && (
        <div className="fixed inset-x-0 bottom-0 z-10 border-t border-line bg-white p-3">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2">
            <span>{chosen.length} of 3 chosen</span>
            <button type="button" className="btn btn-primary" disabled={chosen.length < 2} onClick={() => navigate(`/colleges/compare?ids=${chosen.join(',')}`)}>
              {chosen.length < 2 ? 'Choose one more' : 'Compare'}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
