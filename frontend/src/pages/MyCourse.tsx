import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type RoadmapDetail, type Skill } from '../api/client'
import { CareerPicker } from '../components/CareerPicker'
import { Notice } from '../components/Form'
import { SkillGap } from '../components/SkillGap'
import { TechChanges } from '../components/TechChanges'
import { useDoneSteps, useMyPath } from '../context/useMyCourse'

export function MyPath() {
  const { slug, from, choose } = useMyPath()
  const { done } = useDoneSteps()
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
        <p className="mt-2 max-w-2xl">Choose a career to start. You don't need an account, and your choice stays in this browser.</p>
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

      <section className="card mt-4">
        <p className="font-semibold">You've finished {finished.length} of {roadmap.steps.length} steps ({percent}%)</p>
        <progress max={100} value={percent} className="mt-2 h-3 w-full accent-teal" aria-label="Path progress" />
      </section>

      <h2 className="mt-8 text-2xl">What to do next</h2>
      {next.length === 0 && <p className="mt-2">You've finished every step. Look at your options below.</p>}
      <ol className="mt-3 grid gap-3">
        {next.map((step) => (
          <li key={step.id} className="card">
            <h3 className="text-lg">{step.title}</h3>
            <p className="mt-1">{step.why}</p>
            {step.build_task && <p className="mt-1 text-sm"><strong>Try this:</strong> {step.build_task}</p>}
          </li>
        ))}
      </ol>
      <div className="mt-3 flex flex-wrap gap-2">
        <Link to={`/roadmaps/${roadmap.slug}${from ? `?${from}` : ''}`} className="btn btn-primary">Open my full path</Link>
        <button type="button" className="btn btn-outline" onClick={() => { choose(''); setRoadmap(null) }}>Change my career</button>
      </div>

      {skills.length > 0 && <SkillGap skills={skills} career={roadmap.name} />}
      <TechChanges roadmap={roadmap.slug} title="What's changing, and what to learn" />
    </div>
  )
}
