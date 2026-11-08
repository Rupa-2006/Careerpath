import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, type ApiError, type CourseDetail, type CourseSummary, type FieldSummary, type RoadmapSummary } from '../api/client'
import { areaOf } from '../components/areas'
import { Notice } from '../components/Form'

const STEPS = ['Area', 'Course', 'Career', 'Path']

function Steps({ current }: { current: number }) {
  return (
    <ol className="mb-5 flex flex-wrap items-center gap-2 text-sm" aria-label="Your progress">
      {STEPS.map((label, index) => (
        <li key={label} aria-current={index === current ? 'step' : undefined} className={`rounded-full px-3 py-1 font-semibold ${index === current ? 'bg-pine text-white' : index < current ? 'bg-pine-soft text-pine' : 'border border-line text-muted'}`}>
          {index + 1}. {label}
        </li>
      ))}
    </ol>
  )
}

/** Step 1: every area of study that has courses. */
export function AreaGrid() {
  const [fields, setFields] = useState<FieldSummary[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.fields().then(setFields).catch((problem: ApiError) => setError(problem.message))
  }, [])

  return (
    <>
      <Notice kind="error">{error}</Notice>
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {fields.filter((field) => field.course_count > 0).map((field) => (
          <li key={field.slug}>
            <Link to={`/choose/${field.slug}`} className="card flex h-full items-start gap-4 border-t-4 text-ink no-underline" style={{ borderTopColor: areaOf(field.slug).colour }}>
              <span aria-hidden="true" className="grid h-12 w-12 shrink-0 place-items-center rounded-xl text-2xl" style={{ background: `${areaOf(field.slug).colour}1a` }}>{areaOf(field.slug).icon}</span>
              <span>
                <span className="block font-bold text-pine">{field.name}</span>
                <span className="mt-1 block text-sm text-muted">{field.tagline}</span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}

export function ChooseArea() {
  return (
    <>
      <Steps current={0} />
      <h1 className="text-3xl">What area interests you?</h1>
      <p className="mb-4 mt-2 text-muted">Pick one to see its courses.</p>
      <AreaGrid />
    </>
  )
}

/** Step 2: the courses and branches in one area. */
export function ChooseCourse() {
  const { field = '' } = useParams()
  const [title, setTitle] = useState('')
  const [courses, setCourses] = useState<CourseSummary[] | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.fields().then((all) => setTitle(all.find((item) => item.slug === field)?.name ?? '')).catch(() => setTitle(''))
    api.courses(`field=${encodeURIComponent(field)}`).then((found) => setCourses(found.courses)).catch((problem: ApiError) => setError(problem.message))
  }, [field])

  return (
    <>
      <Steps current={1} />
      <p><Link to="/choose">← All areas</Link></p>
      <h1 className="mt-2 flex items-center gap-3 text-3xl"><span aria-hidden="true">{areaOf(field).icon}</span>{title || 'Courses'}</h1>
      <p className="mb-4 mt-2 text-muted">Choose a course or branch.</p>
      <Notice kind="error">{error}</Notice>
      {courses === null && !error && <p className="text-muted">Loading…</p>}
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {courses?.map((course) => (
          <li key={course.slug}>
            <Link to={`/choose/${field}/${course.slug}`} className="card block h-full border-l-4 text-ink no-underline" style={{ borderLeftColor: areaOf(field).colour }}>
              <span className="font-bold text-pine">{course.name}</span>
              <span className="mt-1 block text-sm text-muted">{course.summary}</span>
              <span className="mt-1 block text-sm font-semibold text-teal">{course.duration}</span>
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-5 flex flex-wrap gap-x-6 gap-y-2">
        {courses && courses.length >= 2 && <Link to={`/compare?area=${encodeURIComponent(field)}`} className="font-semibold">Not sure? Compare these courses side by side →</Link>}
        <Link to="/all-courses" className="font-semibold">Can't find it? See the full course list →</Link>
      </p>
    </>
  )
}

/** Step 3: the careers a course leads to. A course with one career goes straight to its path. */
export function ChooseCareer() {
  const { field = '', course: slug = '' } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [paths, setPaths] = useState<RoadmapSummary[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.course(slug, '').then((found) => {
      if (found.roadmaps.length === 1) {
        navigate(`/roadmaps/${found.roadmaps[0].slug}?area=${field}&course=${slug}`, { replace: true })
        return
      }
      setCourse(found)
      api.roadmaps('en').then((all) => setPaths(all.filter((item) => found.roadmaps.some((road) => road.slug === item.slug)))).catch(() => setPaths([]))
    }).catch((problem: ApiError) => setError(problem.message))
  }, [slug, navigate])

  if (error) return <Notice kind="error">{error}</Notice>
  if (!course) return <p className="py-10 text-center text-muted">Loading…</p>

  return (
    <>
      <Steps current={2} />
      <p><Link to={`/choose/${field}`}>← Back to courses</Link></p>
      <h1 className="mt-2 text-3xl">{course.name}</h1>
      <p className="mb-4 mt-2 text-muted">What do you want to become with this course?</p>
      {course.roadmaps.length === 0 && <p>We don't have a path for this course yet.</p>}
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {paths.map((item) => (
          <li key={item.slug}>
            <Link to={`/roadmaps/${item.slug}?area=${field}&course=${slug}`} className="card block h-full border-l-4 text-ink no-underline" style={{ borderLeftColor: areaOf(field).colour }}>
              <span className="font-bold text-pine">{item.name}</span>
              <span className="mt-1 block text-sm text-muted">{item.description}</span>
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-5"><Link to={`/courses/${course.slug}`} className="font-semibold">See course details, rules and exams →</Link></p>
    </>
  )
}
