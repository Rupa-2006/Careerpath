import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CourseDetail, type CourseSummary } from '../api/client'
import { areaOf } from '../components/areas'
import { Notice } from '../components/Form'
import { EligibilityBadge } from '../components/Trust'
import { useBackground } from '../context/useBackground'

const MAX = 3

const ROWS: [string, (course: CourseDetail) => React.ReactNode][] = [
  ['What it is', (course) => course.summary],
  ['Duration', (course) => course.duration],
  ['What you study', (course) => course.what_you_study],
  ['Where it can lead', (course) => course.careers.join(', ') || 'Not added yet'],
  ['For you', (course) => <EligibilityBadge eligibility={course.eligibility} />],
  ['Who can join', (course) => course.criteria.map((rule) => `${rule.label}: ${rule.summary}`).join(' ') || 'No confirmed rule yet'],
  ['Entrance', (course) => course.exams.map((exam) => exam.name).join(', ') || 'None listed'],
]

/** Students pick 2 or 3 courses here, so comparing never depends on another page. */
export function Compare() {
  const [params, setParams] = useSearchParams()
  const { query } = useBackground()
  const area = params.get('area') ?? ''
  const slugs = useMemo(() => (params.get('c') ?? '').split(',').filter(Boolean).slice(0, MAX), [params])
  const [options, setOptions] = useState<CourseSummary[]>([])
  const [courses, setCourses] = useState<CourseDetail[]>([])
  const [error, setError] = useState('')
  const colour = areaOf(area).colour

  useEffect(() => {
    const filter = area ? `field=${encodeURIComponent(area)}` : ''
    api.courses(filter).then((found) => setOptions(found.courses)).catch((problem: ApiError) => setError(problem.message))
  }, [area])

  useEffect(() => {
    if (slugs.length >= 2) {
      api.compare(slugs, query).then(setCourses).catch((problem: ApiError) => setError(problem.message))
    }
  }, [slugs, query])
  const showing = slugs.length >= 2 ? courses.filter((course) => slugs.includes(course.slug)) : []

  function toggle(slug: string) {
    const next = slugs.includes(slug) ? slugs.filter((item) => item !== slug) : [...slugs, slug].slice(0, MAX)
    const updated = new URLSearchParams(params)
    if (next.length) updated.set('c', next.join(','))
    else updated.delete('c')
    setParams(updated, { replace: true })
  }

  return (
    <>
      <p><Link to={area ? `/choose/${area}` : '/choose'}>← {area ? 'Back to the courses' : 'Choose an area'}</Link></p>
      <h1 className="mt-2 flex items-center gap-3 text-3xl">
        {area && <span aria-hidden="true">{areaOf(area).icon}</span>}Compare courses
      </h1>
      <p className="mt-2 text-muted">Pick 2 or 3 courses to see them side by side.</p>
      <Notice kind="error">{error}</Notice>

      <ul className="mt-4 flex flex-wrap gap-2" aria-label="Courses to compare">
        {options.map((course) => {
          const picked = slugs.includes(course.slug)
          const full = !picked && slugs.length >= MAX
          return (
            <li key={course.slug}>
              <button
                type="button" aria-pressed={picked} disabled={full} onClick={() => toggle(course.slug)}
                className={`rounded-full border px-3 py-1.5 text-sm font-semibold transition ${picked ? 'text-white' : 'bg-white text-ink hover:border-teal'} ${full ? 'cursor-not-allowed opacity-40' : 'cursor-pointer'}`}
                style={picked ? { background: colour, borderColor: colour } : undefined}
              >
                {picked ? '✓ ' : ''}{course.name}
              </button>
            </li>
          )
        })}
      </ul>

      {slugs.length < 2 && (
        <p className="mt-6 rounded-2xl border border-dashed border-line bg-white p-6 text-center text-muted">
          {slugs.length === 0 ? 'Pick 2 or 3 courses above.' : 'Pick one more course.'}
        </p>
      )}

      {showing.length >= 2 && (
        <>
          <div className="mt-6 overflow-x-auto rounded-2xl border border-line bg-white shadow-sm">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr style={{ background: `${colour}14` }}>
                  <td className="p-3" />
                  {showing.map((course) => (
                    <th key={course.slug} scope="col" className="p-3 text-base">
                      <Link to={`/courses/${course.slug}`}>{course.name}</Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ROWS.map(([label, value]) => (
                  <tr key={label} className="border-t border-line align-top">
                    <th scope="row" className="w-36 p-3 text-pine">{label}</th>
                    {showing.map((course) => <td key={course.slug} className="p-3">{value(course)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 rounded-lg bg-[#fff1d6] p-3 text-sm">Always confirm on the official website before you apply.</p>
        </>
      )}
    </>
  )
}
