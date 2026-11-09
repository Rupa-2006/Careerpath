import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type RoadmapDetail } from '../api/client'
import { AfterRoadmap, CareerNews } from '../components/CareerExtras'
import { Notice } from '../components/Form'
import { TechChanges } from '../components/TechChanges'
import { useAuth } from '../context/AuthContext'
import { shortName, useDoneSteps, useMyPath } from '../context/useMyCourse'

/** A logged-in student's home: the career they chose at sign-up, their next steps, what's changing and where it leads. */
export function PathHome() {
  const { user } = useAuth()
  const { slug, from } = useMyPath()
  const course = new URLSearchParams(from).get('course') ?? ''
  const { done } = useDoneSteps()
  const [roadmap, setRoadmap] = useState<RoadmapDetail | null>(null)
  const [courseName, setCourseName] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (slug) api.roadmap(slug, 'en').then(setRoadmap).catch((problem: ApiError) => setError(problem.message))
  }, [slug])

  useEffect(() => {
    if (course) api.course(course, '').then((found) => setCourseName(found.name)).catch(() => setCourseName(''))
  }, [course])

  if (error) return <Notice kind="error">{error}</Notice>
  if (!roadmap) return <p className="py-10 text-center text-muted">Loading your path…</p>

  const isDone = (id: number, serverDone: boolean) => serverDone || done.includes(id)
  const finished = roadmap.steps.filter((step) => isDone(step.id, step.done)).length
  const percent = roadmap.steps.length ? Math.round((finished * 100) / roadmap.steps.length) : 0
  const next = roadmap.steps.filter((step) => !isDone(step.id, step.done)).slice(0, 2)
  const year = next[0]?.year
  const career = shortName(roadmap.name)

  return (
    <>
      <section className="rounded-2xl bg-pine px-6 py-8 text-white md:px-10">
        <p className="text-sm font-semibold uppercase tracking-wide text-sun">🎯 {user?.name ? `${user.name.split(' ')[0]}'s path` : 'Your path'}</p>
        <h1 className="mt-1 text-3xl text-white md:text-4xl">{roadmap.name}</h1>
        {courseName && <p className="mt-1 text-white/85">Through {courseName}</p>}
        <div className="mt-5 max-w-xl">
          <p className="font-semibold">
            {finished} of {roadmap.steps.length} steps done ({percent}%){year ? ` · Working on Year ${year}` : ' · Path complete 🎓'}
          </p>
          <div className="mt-2 h-3 overflow-hidden rounded-full bg-white/20" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} aria-label="Path progress">
            <div className="h-full rounded-full bg-sun" style={{ width: `${percent}%` }} />
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link to={`/roadmaps/${roadmap.slug}`} className="btn btn-sun">Open my roadmap</Link>
          <Link to="/my-path" className="btn border-2 border-white/60 text-white hover:bg-white/10">My progress</Link>
        </div>
              </section>

      {next.length > 0 && (
        <section className="mt-8">
          <h2 className="text-2xl">Your next {next.length === 1 ? 'step' : 'steps'}</h2>
          <ol className="mt-3 grid gap-3 md:grid-cols-2">
            {next.map((step) => (
              <li key={step.id} className="card">
                <p className="text-xs font-semibold uppercase text-teal">Year {step.year}</p>
                <h3 className="mt-1 text-lg">{step.title}</h3>
                <p className="mt-1">{step.why}</p>
                {step.build_task && <p className="mt-2 rounded-lg bg-[#fff7e6] p-2 text-sm"><strong>Try this:</strong> {step.build_task}</p>}
              </li>
            ))}
          </ol>
          <p className="mt-3"><Link to={`/roadmaps/${roadmap.slug}`} className="font-semibold">See all {roadmap.steps.length} steps and tick them off →</Link></p>
        </section>
      )}

      <TechChanges roadmap={roadmap.slug} title={`What's changing for a ${career}`} />
      <CareerNews roadmap={roadmap.slug} />
      <AfterRoadmap roadmap={roadmap.slug} course={course} title={`Opportunities for a ${career}`} />

      <section className="mt-10 grid gap-3 sm:grid-cols-3">
        <Link to="/skills" className="card block text-ink no-underline">
          <span className="text-2xl" aria-hidden="true">🧠</span>
          <span className="mt-1 block font-bold text-pine">My skills</span>
          <span className="block text-sm text-muted">Only the skills a {career} needs</span>
        </Link>
        <Link to="/scholarships" className="card block text-ink no-underline">
          <span className="text-2xl" aria-hidden="true">🎓</span>
          <span className="mt-1 block font-bold text-pine">Scholarships</span>
          <span className="block text-sm text-muted">Help to pay for your studies</span>
        </Link>
        <Link to="/assistant" className="card block text-ink no-underline">
          <span className="text-2xl" aria-hidden="true">💬</span>
          <span className="mt-1 block font-bold text-pine">Ask about my path</span>
          <span className="block text-sm text-muted">Questions about becoming a {career}</span>
        </Link>
      </section>

      <p className="mt-10 border-t border-line pt-4 text-center text-sm text-muted">
        Want to look around? <Link to="/choose" className="font-semibold">Explore other careers</Link>
      </p>
    </>
  )
}
