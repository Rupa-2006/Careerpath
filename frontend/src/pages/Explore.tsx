import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type FieldSummary } from '../api/client'
import { BackgroundForm } from '../components/BackgroundForm'
import { Notice } from '../components/Form'
import { TrustBadge } from '../components/Trust'
import { useBackground } from '../context/useBackground'

export function Explore() {
  const background = useBackground()
  const [fields, setFields] = useState<FieldSummary[] | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.fields().then(setFields).catch((problem: ApiError) => setError(problem.message))
  }, [])

  return (
    <>
      <h1 className="text-3xl">Explore your opportunities</h1>
      <p className="mb-4 mt-2 max-w-2xl text-muted">Tell us about you, and we'll check courses against your subjects. You can also skip this and just look around.</p>
      <div className="max-w-3xl"><BackgroundForm state={background} /></div>
      <p className="mt-4 rounded-lg bg-pine-soft p-3">
        Not sure where to start? <Link to="/quiz" className="font-semibold">Take the 2-minute quiz →</Link>
      </p>

      <section className="mt-8">
        <h2 className="text-2xl">All the fields you can explore</h2>
        <p className="mt-2 max-w-2xl text-muted">Not every field is open to every student. Open a field to see what it means and who can join.</p>
        <Notice kind="error">{error}</Notice>
        {fields?.length === 0 && <p className="mt-4 text-muted">Fields are being checked and will appear here once reviewed.</p>}
        <ul className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {fields?.map((field) => (
            <li key={field.slug}>
              <Link to={`/explore/${field.slug}`} className="card block h-full text-ink no-underline hover:border-teal">
                <h3 className="text-lg">{field.name}</h3>
                <p className="mt-1 text-muted">{field.tagline}</p>
                <p className="mt-2 flex flex-wrap items-center gap-2 text-sm font-semibold text-teal">
                  {field.course_count > 0 ? `${field.course_count} ${field.course_count === 1 ? 'path' : 'paths'}` : 'Courses being added'}
                  <TrustBadge status={field.status} />
                </p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}
