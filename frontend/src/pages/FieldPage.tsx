import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, type ApiError, type FieldDetail } from '../api/client'
import { Notice } from '../components/Form'
import { CourseCard, SourceLine, TrustBadge } from '../components/Trust'
import { useBackground } from '../context/useBackground'

export function FieldPage() {
  const { slug = '' } = useParams()
  const { query } = useBackground()
  const [field, setField] = useState<FieldDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.field(slug, query).then(setField).catch((problem: ApiError) => setError(problem.message))
  }, [slug, query])

  if (error) return <Notice kind="error">{error}</Notice>
  if (!field) return <p className="py-10 text-center text-muted">Loading…</p>

  const sections = [
    ['What is this field?', field.what_is_it],
    ['What will you learn?', field.what_you_learn],
    ['Who can choose it?', field.who_can_choose],
    ['Skills that help', field.required_skills],
    ['Further education', field.further_education],
  ]

  return (
    <>
      <p><Link to="/explore">← All fields</Link></p>
      <h1 className="mt-2 text-3xl">{field.name}</h1>
      <p className="mt-1 text-lg text-muted">{field.tagline}</p>
      <p className="mt-2"><TrustBadge status={field.status} /></p>

      <dl className="mt-6 grid gap-4 md:grid-cols-2">
        {sections.map(([title, text]) => (
          <div key={title} className="card">
            <dt className="font-bold text-pine">{title}</dt>
            <dd className="mt-1">{text}</dd>
          </div>
        ))}
      </dl>
      <div className="mt-3"><SourceLine record={field} /></div>

      <h2 className="mt-8 text-2xl">Paths in this field</h2>
      {field.courses.length === 0
        ? <p className="mt-2 text-muted">We haven't added courses here yet, because we only list what we can source.</p>
        : <ul className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{field.courses.map((course) => <CourseCard key={course.slug} course={course} />)}</ul>}
    </>
  )
}
