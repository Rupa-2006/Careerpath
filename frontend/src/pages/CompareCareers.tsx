import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  api, type ApiError, type CareerGrowth, type CareerOpportunity, type RoadmapDetail, type RoadmapSummary, type Skill, type TechChange,
} from '../api/client'
import { Notice } from '../components/Form'
import { useMyPath } from '../context/useMyCourse'

type Career = {
  roadmap: RoadmapDetail
  growth: CareerGrowth | null
  skills: Skill[]
  changes: TechChange[]
  opportunities: CareerOpportunity[]
}

async function loadCareer(slug: string): Promise<Career> {
  const [roadmap, growth, skills, changes, opportunities] = await Promise.all([
    api.roadmap(slug, 'en'),
    api.careerGrowth(slug).catch(() => null),
    api.skills('en', slug).catch(() => [] as Skill[]),
    api.techChanges(slug).catch(() => [] as TechChange[]),
    api.careerOpportunities(slug).catch(() => [] as CareerOpportunity[]),
  ])
  return { roadmap, growth, skills, changes, opportunities }
}

const none = <span className="text-muted">Not added yet</span>

const ROWS: [string, (career: Career) => React.ReactNode][] = [
  ['What the work is', ({ roadmap }) => roadmap.description],
  ['Courses that lead here', ({ roadmap }) => roadmap.courses.length ? roadmap.courses.join(', ') : none],
  ['Length of the path', ({ roadmap }) => `${roadmap.years} year${roadmap.years > 1 ? 's' : ''}, ${roadmap.steps.length} steps`],
  ['Where you start', ({ roadmap }) => roadmap.steps[0] ? <>{roadmap.steps[0].title}<span className="block text-xs text-muted">Year {roadmap.steps[0].year}</span></> : none],
  ['How you grow', ({ growth }) => growth
    ? <ol className="grid gap-1"><li>1. {growth.first}</li><li>2. {growth.next}</li><li>3. {growth.senior}</li></ol>
    : none],
  ['Skills it needs most', ({ skills }) => {
    const own = skills.filter((skill) => !skill.for_all).slice(0, 6)
    return own.length ? <ul className="flex flex-wrap gap-1">{own.map((skill) => <li key={skill.slug} className="rounded-full bg-pine-soft px-2 py-0.5 text-xs">{skill.name}</li>)}</ul> : none
  }],
  ["What's changing", ({ changes }) => changes.length
    ? <ul className="grid gap-1">{changes.map((change) => <li key={change.slug}>• {change.title}</li>)}</ul>
    : none],
  ['Where to find opportunities', ({ opportunities }) => opportunities.length
    ? <ul className="grid gap-1">{opportunities.slice(0, 4).map((item) => <li key={item.title}><a href={item.url} target="_blank" rel="noopener noreferrer">{item.title} ↗</a></li>)}</ul>
    : none],
]

/** Two careers side by side, so a student can see how the paths really differ before choosing one. */
export function CompareCareers() {
  const [params, setParams] = useSearchParams()
  const { slug: myPath, choose, fixed } = useMyPath()
  const a = params.get('a') ?? myPath
  const b = params.get('b') ?? ''
  const [all, setAll] = useState<RoadmapSummary[]>([])
  const [careers, setCareers] = useState<Record<string, Career>>({})
  const [error, setError] = useState('')

  useEffect(() => {
    api.roadmaps('en').then(setAll).catch((problem: ApiError) => setError(problem.message))
  }, [])

  useEffect(() => {
    for (const slug of [a, b]) {
      if (slug && !careers[slug]) {
        loadCareer(slug)
          .then((career) => setCareers((current) => ({ ...current, [slug]: career })))
          .catch((problem: ApiError) => setError(problem.message))
      }
    }
  }, [a, b, careers])

  function pick(side: 'a' | 'b', slug: string) {
    const updated = new URLSearchParams(params)
    updated.set('a', a)
    if (slug) updated.set(side, slug)
    else updated.delete(side)
    setParams(updated, { replace: true })
  }

  const shown = [a, b].filter(Boolean).map((slug) => careers[slug]).filter((career): career is Career => Boolean(career))
  const ready = a && b && a !== b && shown.length === 2

  const picker = (side: 'a' | 'b', value: string, label: string) => (
    <label className="flex-1">
      <span className="mb-1 block font-semibold">{label}</span>
      <select className="input" value={value} onChange={(event) => pick(side, event.target.value)}>
        <option value="">Choose a career</option>
        {all.map((item) => (
          <option key={item.slug} value={item.slug} disabled={item.slug === (side === 'a' ? b : a)}>
            {item.name}{item.slug === myPath ? ' (my path)' : ''}
          </option>
        ))}
      </select>
    </label>
  )

  return (
    <>
      <h1 className="text-3xl">Compare two careers</h1>
      <p className="mt-2 max-w-2xl text-muted">See two paths side by side: how long they take, how you grow, what skills they need and what is changing.</p>
      <Notice kind="error">{error}</Notice>

      <div className="card mt-4 flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-end">
        {picker('a', a, 'First career')}
        <span aria-hidden="true" className="hidden pb-3 text-center font-bold text-muted sm:block">vs</span>
        {picker('b', b, 'Second career')}
      </div>

      {!(a && b) && (
        <p className="mt-6 rounded-2xl border border-dashed border-line bg-white p-6 text-center text-muted">
          {a || b ? 'Choose one more career.' : 'Choose two careers above.'}
        </p>
      )}
      {a && b && !ready && !error && <p className="mt-6 text-center text-muted">Loading…</p>}

      {ready && (
        <>
          <div className="mt-6 overflow-x-auto rounded-2xl border border-line bg-white shadow-sm">
            <table className="w-full min-w-[640px] table-fixed text-left text-sm">
              <thead className="bg-pine-soft">
                <tr>
                  <td className="w-40 p-3" />
                  {shown.map(({ roadmap }) => (
                    <th key={roadmap.slug} scope="col" className="p-3 text-base">
                      <Link to={`/roadmaps/${roadmap.slug}`}>{roadmap.name}</Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ROWS.map(([label, value]) => (
                  <tr key={label} className="border-t border-line align-top">
                    <th scope="row" className="p-3 text-pine">{label}</th>
                    {shown.map((career) => <td key={career.roadmap.slug} className="p-3">{value(career)}</td>)}
                  </tr>
                ))}
                <tr className="border-t border-line">
                  <td className="p-3" />
                  {shown.map(({ roadmap }) => (
                    <td key={roadmap.slug} className="p-3">
                      {roadmap.slug === myPath
                        ? <span className="font-semibold text-teal">✓ This is my path</span>
                        : !fixed && <button type="button" className="btn btn-outline !min-h-9 !py-1 text-sm" onClick={() => choose(roadmap.slug)}>Make this my path</button>}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
          <p className="mt-3 rounded-lg bg-[#fff1d6] p-3 text-sm">
            Both paths are general guidance. Talk to someone working in each field, and confirm course rules on the official website.
          </p>
        </>
      )}
    </>
  )
}
