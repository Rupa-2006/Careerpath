import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CourseDetail } from '../api/client'
import { Notice } from '../components/Form'
import { EligibilityBadge, TrustBadge } from '../components/Trust'
import { useBackground } from '../context/useBackground'

const ROWS: [string, (course: CourseDetail) => React.ReactNode][] = [
  ['Field', (course) => course.field_name],
  ['Type', (course) => course.kind],
  ['For you', (course) => <EligibilityBadge eligibility={course.eligibility} />],
  ['What it is', (course) => course.summary],
  ['Duration', (course) => course.duration],
  ['Who can join', (course) => course.criteria.map((rule) => `${rule.label}: ${rule.summary}`).join(' ') || 'No confirmed rule yet'],
  ['Entrance exams', (course) => course.exams.map((exam) => exam.name).join(', ') || 'None listed'],
  ['What you study', (course) => course.what_you_study],
  ['Where it can lead', (course) => course.careers.join(', ') || 'Not added yet'],
  ['Review status', (course) => <TrustBadge status={course.status} />],
]

export function Compare() {
  const [params] = useSearchParams()
  const { query } = useBackground()
  const [courses, setCourses] = useState<CourseDetail[]>([])
  const [error, setError] = useState('')
  const slugs = useMemo(() => (params.get('c') ?? '').split(',').filter(Boolean), [params])

  useEffect(() => {
    if (slugs.length >= 2) {
      api.compare(slugs, query).then(setCourses).catch((problem: ApiError) => setError(problem.message))
    }
  }, [slugs, query])

  if (slugs.length < 2) {
    return (
      <div className="py-10 text-center">
        <h1 className="text-3xl">Compare courses</h1>
        <p className="mt-2 text-muted">Tick 2 or 3 courses on the Courses page to compare them.</p>
        <Link to="/choose" className="btn btn-primary mt-4">Choose an area</Link>
      </div>
    )
  }

  return (
    <>
      <p><Link to="/choose">← Choose an area</Link></p>
      <h1 className="mt-2 text-3xl">Compare courses</h1>
      <Notice kind="error">{error}</Notice>
      <div className="mt-4 overflow-x-auto rounded-xl border border-line bg-white">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="bg-pine-soft">
            <tr>
              <td className="p-3" />
              {courses.map((course) => (
                <th key={course.slug} scope="col" className="p-3"><Link to={`/courses/${course.slug}`}>{course.name}</Link></th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(([label, value]) => (
              <tr key={label} className="border-t border-line align-top">
                <th scope="row" className="w-36 p-3 text-pine">{label}</th>
                {courses.map((course) => <td key={course.slug} className="p-3">{value(course)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 rounded-lg bg-[#fff1d6] p-3 text-sm">Always confirm on the official website before you apply.</p>
    </>
  )
}
