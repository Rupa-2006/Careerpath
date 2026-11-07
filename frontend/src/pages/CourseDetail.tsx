import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, type ApiError, type CourseDetail, type Criterion } from '../api/client'
import { Notice } from '../components/Form'
import { ReportForm } from '../components/Journey'
import { EligibilityNote, SourceLine, TrustBadge } from '../components/Trust'
import { useBackground } from '../context/useBackground'
import { useMyPath } from '../context/useMyCourse'

function Rule({ rule }: { rule: Criterion }) {
  const marks = rule.min_percentage && `At least ${rule.min_percentage}%${rule.min_percentage_reserved ? ` (${rule.min_percentage_reserved}% for some reserved categories)` : ''}`
  const age = rule.min_age && `Age ${rule.min_age}${rule.max_age ? ` to ${rule.max_age}` : ' or older'}`
  return (
    <li className="card">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg">{rule.label}</h3>
        <TrustBadge status={rule.status} />
      </div>
      <p className="mt-1">{rule.summary}</p>
      {rule.groups.length > 0 && <p className="mt-1 text-sm"><strong>Subjects:</strong> {rule.groups.flatMap((group) => group.subjects).join(' + ')}</p>}
      {(marks || age) && <p className="mt-1 text-sm">{[marks, age].filter(Boolean).join(' · ')}</p>}
      {rule.regions.length > 0 && <p className="mt-1 text-sm text-muted">Applies in: {rule.regions.join(', ')}</p>}
      <div className="mt-2"><SourceLine record={rule} /></div>
    </li>
  )
}

export function CourseDetailPage() {
  const { slug = '' } = useParams()
  const { query } = useBackground()
  const { slug: mine, choose } = useMyPath()
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.course(slug, query).then(setCourse).catch((problem: ApiError) => setError(problem.message))
  }, [slug, query])

  if (error) return <Notice kind="error">{error}</Notice>
  if (!course) return <p className="py-10 text-center text-muted">Loading…</p>

  return (
    <div className="mx-auto max-w-4xl">
      <p><Link to={`/choose/${course.field_slug}`}>← {course.field_name}</Link></p>
      <p className="mt-3 text-sm text-muted">{course.kind}</p>
      <h1 className="mt-1 text-3xl">{course.name}</h1>
      <p className="mt-2"><TrustBadge status={course.status} /></p>
      <p className="mt-3 text-lg">{course.summary}</p>

      <div className="mt-4"><EligibilityNote eligibility={course.eligibility} /></div>

      <dl className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="card"><dt className="font-bold text-pine">Duration</dt><dd className="mt-1">{course.duration}</dd></div>
        <div className="card"><dt className="font-bold text-pine">How admission works</dt><dd className="mt-1">{course.admission}</dd></div>
        <div className="card"><dt className="font-bold text-pine">What you will study</dt><dd className="mt-1">{course.what_you_study}</dd></div>
        <div className="card"><dt className="font-bold text-pine">Where it can lead</dt><dd className="mt-1">{course.careers.join(', ') || 'Not added yet'}</dd></div>
      </dl>

      <h2 className="mt-8 text-2xl">Who can join</h2>
      {course.criteria.length === 0
        ? <p className="mt-2 text-muted">We don't have a confirmed rule yet. Ask the college or check the official site.</p>
        : <ul className="mt-3 grid gap-3">{course.criteria.map((rule) => <Rule key={rule.label} rule={rule} />)}</ul>}

      {course.exams.length > 0 && (
        <>
          <h2 className="mt-8 text-2xl">Entrance exams</h2>
          <ul className="mt-3 grid gap-3 md:grid-cols-2">
            {course.exams.map((exam) => (
              <li key={exam.slug} className="card">
                <h3 className="text-lg">{exam.name}</h3>
                <p className="text-sm text-muted">{exam.conducted_by}{exam.region ? ` · ${exam.region.name} only` : ' · National'}</p>
                <p className="mt-1">{exam.summary}</p>
                <div className="mt-2"><SourceLine record={exam} /></div>
              </li>
            ))}
          </ul>
        </>
      )}

      {course.roadmaps.length > 0 && (
        <>
          <h2 className="mt-8 text-2xl">Year-by-year roadmaps</h2>
          <ul className="mt-2 flex flex-wrap gap-2">
            {course.roadmaps.map((item) => <li key={item.slug}><Link to={`/roadmaps/${item.slug}`} className="btn btn-outline">{item.name} →</Link></li>)}
          </ul>
        </>
      )}
      {course.roadmaps[0] && (
        <p className="mt-6">
          {mine === course.roadmaps[0].slug
            ? <Link to="/my-path" className="btn btn-primary">Open My Path</Link>
            : <button type="button" className="btn btn-primary" onClick={() => choose(course.roadmaps[0].slug, `area=${course.field_slug}&course=${course.slug}`)}>Make this my path</button>}
        </p>
      )}
      <div className="mt-4"><SourceLine record={course} /></div>
      <p className="mt-2 rounded-lg bg-[#fff1d6] p-3 text-sm">Rules change every year. Always confirm on the official website before you apply. A match here is not a promise of admission.</p>
      <ReportForm />
    </div>
  )
}
