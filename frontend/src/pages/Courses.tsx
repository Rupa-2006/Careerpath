import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CourseSummary, type FieldSummary } from '../api/client'
import { BackgroundForm } from '../components/BackgroundForm'
import { Field, Notice } from '../components/Form'
import { CourseCard } from '../components/Trust'
import { useBackground } from '../context/useBackground'

export function Courses() {
  const background = useBackground()
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const [courses, setCourses] = useState<CourseSummary[] | null>(null)
  const [fields, setFields] = useState<FieldSummary[]>([])
  const [text, setText] = useState(params.get('q') ?? '')
  const [compare, setCompare] = useState<string[]>([])
  const [error, setError] = useState('')

  const search = params.get('q') ?? ''
  const field = params.get('field') ?? ''
  const openToMe = params.get('open') === '1'

  useEffect(() => {
    api.fields().then(setFields).catch(() => setFields([]))
  }, [])

  useEffect(() => {
    const query = new URLSearchParams(background.query)
    if (search) query.set('q', search)
    if (field) query.set('field', field)
    if (openToMe) query.set('open_to_me', 'true')
    api.courses(query.toString())
      .then((result) => setCourses(result.courses))
      .catch((problem: ApiError) => setError(problem.message))
  }, [background.query, search, field, openToMe])

  function setParam(name: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(name, value)
    else next.delete(name)
    setParams(next, { replace: true })
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    setParam('q', text.trim())
  }

  function toggle(slug: string) {
    setCompare((items) => {
      if (items.includes(slug)) return items.filter((item) => item !== slug)
      return items.length < 3 ? [...items, slug] : items
    })
  }

  return (
    <>
      <h1 className="text-3xl">Courses after Class 12</h1>
      <p className="mb-4 mt-2 max-w-2xl text-muted">You don't need to know your stream or career. Search, or add your details to check what fits.</p>
      <p className="mb-4"><Link to="/all-courses" className="font-semibold">See the full course list →</Link></p>
      <BackgroundForm state={background} />

      <div className="card mt-4 grid items-end gap-x-4 md:grid-cols-3">
        <form onSubmit={submit} className="md:col-span-2">
          <Field label="Search courses">
            <span className="flex gap-2">
              <input className="input" type="search" maxLength={100} placeholder="For example: pilot, law, medicines" value={text} onChange={(event) => setText(event.target.value)} />
              <button type="submit" className="btn btn-primary">Search</button>
            </span>
          </Field>
        </form>
        <Field label="Field">
          <select className="input" value={field} onChange={(event) => setParam('field', event.target.value)}>
            <option value="">All fields</option>
            {fields.map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
          </select>
        </Field>
        <label className="flex min-h-11 items-center gap-2 md:col-span-3">
          <input type="checkbox" checked={openToMe} onChange={(event) => setParam('open', event.target.checked ? '1' : '')} />
          Hide courses that don't fit my subjects
        </label>
      </div>

      <Notice kind="error">{error}</Notice>
      {courses && <p className="mt-4 font-semibold">{courses.length} {courses.length === 1 ? 'course' : 'courses'}</p>}
      {courses?.length === 0 && <p className="mt-2 text-muted">No courses match yet. Try fewer filters. New courses appear once they've been reviewed.</p>}
      <ul className="mt-3 grid gap-4 pb-20 md:grid-cols-2 lg:grid-cols-3">
        {courses?.map((course) => (
          <CourseCard key={course.slug} course={course} selected={compare.includes(course.slug)} onToggle={() => toggle(course.slug)} />
        ))}
      </ul>

      {compare.length > 0 && (
        <div className="fixed inset-x-0 bottom-0 z-10 border-t border-line bg-white p-3">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2">
            <span>{compare.length} of 3 chosen{compare.length === 3 ? ' (the most you can compare)' : ''}</span>
            <button
              type="button"
              className="btn btn-primary"
              disabled={compare.length < 2}
              onClick={() => navigate(`/compare?c=${compare.join(',')}`)}
            >
              {compare.length < 2 ? 'Choose one more' : 'Compare'}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
