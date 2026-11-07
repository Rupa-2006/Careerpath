import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, type ApiError, type CollegeDetail, type CourseSummary, type Fact } from '../api/client'
import { CollegeAttribution } from '../components/CollegeAttribution'
import { Field, Notice } from '../components/Form'
import { SourceLine } from '../components/Trust'
import { useAuth } from '../context/AuthContext'

const FACT_LABELS: [Fact['kind'], string][] = [
  ['admission', 'Admission process'],
  ['fees', 'Fees'],
  ['placements', 'Placements'],
  ['facilities', 'Facilities'],
]
const NOT_AVAILABLE = "Not available. We only show this when it comes from an official source."

function AddInformation({ college, onSaved }: { college: CollegeDetail; onSaved: () => void }) {
  const [kind, setKind] = useState('course')
  const [courses, setCourses] = useState<CourseSummary[]>([])
  const [courseSlug, setCourseSlug] = useState('')
  const [branch, setBranch] = useState('')
  const [value, setValue] = useState('')
  const [year, setYear] = useState('2026-27')
  const [sourceName, setSourceName] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.courses('').then((result) => setCourses(result.courses)).catch(() => setCourses([]))
  }, [])

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    const sourced = { academic_year: year, source_name: sourceName, source_url: sourceUrl }
    try {
      if (kind === 'course') await api.addOffering(college.id, { ...sourced, course_slug: courseSlug, branch })
      else if (kind === 'website') await api.setWebsite(college.id, value)
      else await api.addFact(college.id, { ...sourced, kind, value })
      setValue('')
      setBranch('')
      onSaved()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  return (
    <form onSubmit={submit} className="card mt-8 border-teal">
      <h2 className="text-xl">Admin: add checked information</h2>
      <p className="mb-3 text-sm text-muted">Only add what you have read on an official page. It goes live straight away.</p>
      <Notice kind="error">{error}</Notice>
      <Field label="What are you adding?">
        <select className="input" value={kind} onChange={(event) => { setKind(event.target.value); setValue('') }}>
          <option value="course">Course offered</option>
          <option value="website">Official website</option>
          {FACT_LABELS.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
        </select>
      </Field>
      {kind === 'course' && (
        <>
          <Field label="Course">
            <select className="input" required value={courseSlug} onChange={(event) => setCourseSlug(event.target.value)}>
              <option value="">Choose a course</option>
              {courses.map((course) => <option key={course.slug} value={course.slug}>{course.name}</option>)}
            </select>
          </Field>
          <Field label="Branch (optional)">
            <input className="input" maxLength={150} value={branch} onChange={(event) => setBranch(event.target.value)} />
          </Field>
        </>
      )}
      {kind === 'website' && (
        <Field label="Website address">
          <input className="input" type="url" required value={value} onChange={(event) => setValue(event.target.value)} />
        </Field>
      )}
      {kind !== 'course' && kind !== 'website' && (
        <Field label="Details">
          <textarea className="input" required minLength={3} maxLength={2000} rows={3} value={value} onChange={(event) => setValue(event.target.value)} />
        </Field>
      )}
      {kind !== 'website' && (
        <div className="grid gap-x-4 sm:grid-cols-3">
          <Field label="Academic year">
            <input className="input" required pattern="20[0-9]{2}-[0-9]{2}" value={year} onChange={(event) => setYear(event.target.value)} />
          </Field>
          <Field label="Source name">
            <input className="input" required minLength={3} maxLength={200} value={sourceName} onChange={(event) => setSourceName(event.target.value)} />
          </Field>
          <Field label="Source link">
            <input className="input" type="url" required value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} />
          </Field>
        </div>
      )}
      <button type="submit" className="btn btn-primary">Add</button>
    </form>
  )
}

export function CollegeDetailPage() {
  const { id = '' } = useParams()
  const { user } = useAuth()
  const [college, setCollege] = useState<CollegeDetail | null>(null)
  const [error, setError] = useState('')
  const isAdmin = user?.role === 'admin'

  const reload = useCallback(() => {
    api.college(id).then(setCollege).catch((problem: ApiError) => setError(problem.message))
  }, [id])

  useEffect(reload, [reload])

  async function remove(action: () => Promise<void>) {
    try {
      await action()
      reload()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  if (error) return <Notice kind="error">{error}</Notice>
  if (!college) return <p className="py-10 text-center text-muted">Loading…</p>

  const basics: [string, string | number | null][] = [
    ['State or UT', college.region.name],
    ['District', college.district],
    ['Year established', college.year_established],
    ['Area', college.location],
    ['College type', college.college_type],
    ['Management', college.management],
    ['Affiliated university', college.university_name],
    ['University type', college.university_type],
    ['AISHE code', college.aishe_code],
  ]

  return (
    <div className="mx-auto max-w-4xl">
      <p><Link to="/colleges">← All colleges</Link></p>
      <h1 className="mt-2 text-3xl">{college.name}</h1>

      <dl className="card mt-4 grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {basics.map(([label, value]) => (
          <div key={label}>
            <dt className="text-sm text-muted">{label}</dt>
            <dd className="font-semibold">{value ?? 'Not listed'}</dd>
          </div>
        ))}
      </dl>
      <div className="mt-2"><SourceLine record={college} /></div>

      <h2 className="mt-8 text-2xl">Official website</h2>
      {college.website
        ? <p className="mt-1"><a href={college.website} target="_blank" rel="noopener noreferrer">{college.website} ↗</a></p>
        : <p className="mt-1 text-muted">{NOT_AVAILABLE}</p>}

      <h2 className="mt-8 text-2xl">Courses and branches</h2>
      {college.offerings.length === 0
        ? <p className="mt-1 text-muted">{NOT_AVAILABLE} Check the college's own website.</p>
        : (
          <ul className="mt-2 grid gap-2">
            {college.offerings.map((item) => (
              <li key={item.id} className="card">
                <Link to={`/courses/${item.course_slug}`} className="font-semibold">{item.course_name}</Link>
                {item.branch && <span> · {item.branch}</span>}
                <SourceLine record={item} />
                {isAdmin && <button type="button" className="mt-1 cursor-pointer text-sm text-danger underline" onClick={() => remove(() => api.deleteOffering(item.id))}>Remove</button>}
              </li>
            ))}
          </ul>
        )}

      {FACT_LABELS.map(([kind, label]) => {
        const facts = college.facts.filter((fact) => fact.kind === kind)
        return (
          <section key={kind}>
            <h2 className="mt-8 text-2xl">{label}</h2>
            {facts.length === 0
              ? <p className="mt-1 text-muted">{NOT_AVAILABLE}</p>
              : (
                <ul className="mt-2 grid gap-2">
                  {facts.map((fact) => (
                    <li key={fact.id} className="card">
                      <p className="whitespace-pre-line">{fact.value}</p>
                      <SourceLine record={fact} />
                      {isAdmin && <button type="button" className="mt-1 cursor-pointer text-sm text-danger underline" onClick={() => remove(() => api.deleteFact(fact.id))}>Remove</button>}
                    </li>
                  ))}
                </ul>
              )}
          </section>
        )
      })}

      {isAdmin && <AddInformation college={college} onSaved={reload} />}
      <CollegeAttribution />
    </div>
  )
}
