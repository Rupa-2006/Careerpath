import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type RoadmapDetail, type Skill } from '../api/client'
import { AfterRoadmap, CareerNews } from '../components/CareerExtras'
import { CareerPicker } from '../components/CareerPicker'
import { Notice } from '../components/Form'
import { ProgressTracker } from '../components/ProgressTracker'
import { SkillGap } from '../components/SkillGap'
import { TechChanges } from '../components/TechChanges'
import { useAuth } from '../context/AuthContext'
import { useDoneSteps, useMyPath, useMySkills } from '../context/useMyCourse'

function SaveBanner() {
  const { user, loading } = useAuth()
  if (user || loading) return null
  return (
    <p className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2 rounded-lg bg-[#fff7e6] p-3 text-sm print:hidden">
      <span>💾 Your progress is saved only on this device.</span>
      <Link to="/login" className="font-semibold">Log in</Link>
      <Link to="/register" className="font-semibold">Sign up free</Link>
      <span className="text-muted">to keep it on every device.</span>
    </p>
  )
}

const TABS = [
  ['next', 'Next steps'],
  ['progress', 'My progress'],
  ['skills', 'My skills'],
  ['changes', "What's changing"],
  ['opportunities', 'Opportunities'],
] as const
type Tab = (typeof TABS)[number][0]

/** Everything about the student's own path, on one page. */
export function MyPath() {
  const [params, setParams] = useSearchParams()
  const tab: Tab = TABS.some(([key]) => key === params.get('tab')) ? params.get('tab') as Tab : 'next'
  const { slug, from, choose, fixed } = useMyPath()
  const { done } = useDoneSteps()
  const { have, toggle } = useMySkills()
  const [roadmap, setRoadmap] = useState<RoadmapDetail | null>(null)
  const [skills, setSkills] = useState<Skill[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (!slug) return
    const fail = (problem: ApiError) => setError(problem.message)
    api.roadmap(slug, 'en').then(setRoadmap).catch(fail)
    api.skills('en', slug).then(setSkills).catch(fail)
  }, [slug])

  if (!slug) {
    return (
      <>
        <h1 className="text-3xl">My Path</h1>
        <p className="mt-2 max-w-2xl">Choose a career to start. You can use My Path without an account, or log in to keep your progress on every device.</p>
        <SaveBanner />
        <div className="mt-4"><CareerPicker /></div>
      </>
    )
  }
  if (error) return <Notice kind="error">{error}</Notice>
  if (!roadmap) return <p className="py-10 text-center text-muted">Loading…</p>

  const finished = roadmap.steps.filter((step) => done.includes(step.id) || step.done)
  const next = roadmap.steps.filter((step) => !done.includes(step.id) && !step.done).slice(0, 3)
  const percent = roadmap.steps.length ? Math.round((finished.length * 100) / roadmap.steps.length) : 0

  return (
    <div className="mx-auto max-w-4xl">
      <p className="text-sm text-muted">My Path</p>
      <h1 className="text-3xl">{roadmap.name}</h1>
      <p className="mt-2">{roadmap.description}</p>
      <SaveBanner />

      <p className="mt-3 font-semibold">{finished.length} of {roadmap.steps.length} steps done ({percent}%)</p>
      <progress max={100} value={percent} className="mt-1 h-3 w-full accent-teal" aria-label="Path progress" />

      <div role="tablist" aria-label="My Path" className="mt-6 flex gap-1 overflow-x-auto border-b border-line print:hidden">
        {TABS.map(([key, label]) => (
          <button
            key={key} type="button" role="tab" aria-selected={tab === key}
            onClick={() => setParams(key === 'next' ? {} : { tab: key }, { replace: true })}
            className={`-mb-px shrink-0 cursor-pointer border-b-2 px-3 py-2 text-sm font-semibold ${tab === key ? 'border-teal text-pine' : 'border-transparent text-muted hover:text-pine'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'next' && (
        <section role="tabpanel">
          {next.length === 0 && <p className="mt-4">You've finished every step. Look at your opportunities.</p>}
          <ol className="mt-4 grid gap-3">
            {next.map((step) => (
              <li key={step.id} className="card">
                <p className="text-xs font-semibold uppercase text-teal">Year {step.year}</p>
                <h3 className="text-lg">{step.title}</h3>
                <p className="mt-1">{step.why}</p>
                {step.build_task && <p className="mt-1 text-sm"><strong>Try this:</strong> {step.build_task}</p>}
              </li>
            ))}
          </ol>
          <div className="mt-3 flex flex-wrap gap-2">
            <Link to={`/roadmaps/${roadmap.slug}${from ? `?${from}` : ''}`} className="btn btn-primary">Open my full roadmap</Link>
            <Link to={`/compare-careers?a=${roadmap.slug}`} className="btn btn-outline">Compare with another career</Link>
            {!fixed && <button type="button" className="btn btn-outline" onClick={() => { choose(''); setRoadmap(null) }}>Change my career</button>}
          </div>
        </section>
      )}
      {tab === 'progress' && <ProgressTracker roadmap={roadmap} done={done} skills={skills} have={have} />}
      {tab === 'skills' && (
        skills.length > 0
          ? <SkillGap skills={skills} career={roadmap.name} have={have} toggle={toggle} />
          : <p className="mt-4 text-muted">No skills added for this career yet.</p>
      )}
      {tab === 'changes' && (
        <>
          <TechChanges roadmap={roadmap.slug} title="What's changing, and what to learn" />
          <CareerNews roadmap={roadmap.slug} />
        </>
      )}
      {tab === 'opportunities' && <AfterRoadmap roadmap={roadmap.slug} course={new URLSearchParams(from).get('course') ?? ''} title="Where your path can take you" />}
    </div>
  )
}
