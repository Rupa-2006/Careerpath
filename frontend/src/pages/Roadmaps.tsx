import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CourseDetail, type RoadmapDetail, type RoadmapStep } from '../api/client'
import { AfterRoadmap, CareerLadder, CareerNews, EmptyChanges } from '../components/CareerExtras'
import { CareerPicker } from '../components/CareerPicker'
import { Notice } from '../components/Form'
import { ReportForm } from '../components/Journey'
import { TechChanges } from '../components/TechChanges'
import { SourceLine } from '../components/Trust'
import { useAuth } from '../context/AuthContext'
import { useLang } from '../context/Language'
import { useDoneSteps, useMyPath } from '../context/useMyCourse'

export function Roadmaps() {
  return (
    <>
      <h1 className="text-3xl">Career paths</h1>
      <p className="mt-2 max-w-2xl text-muted">Choose a career to see the path, what's changing, and where it can take you.</p>
      <div className="mt-4"><CareerPicker /></div>
    </>
  )
}

function Step({ step, onToggle }: { step: RoadmapStep; onToggle: () => void }) {
  const { t } = useLang()
  return (
    <li id={`step-${step.id}`} className={`card scroll-mt-20 border-l-4 ${step.done ? 'border-l-[#2e7d32] bg-[#f4fbf5]' : 'border-l-teal'}`}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="flex-1 basis-56 text-lg">{step.title}</h3>
        <button type="button" onClick={onToggle} className={`btn !min-h-9 !px-3 !py-1 text-sm ${step.done ? 'btn-primary' : 'btn-outline'}`}>
          {step.done ? t('done_undo') : t('mark_done')}
        </button>
      </div>
      <p className="mt-2"><strong>Do this:</strong> {step.build_task}</p>
      <details className="mt-2">
        <summary className="cursor-pointer text-sm font-semibold text-teal">Why this matters, and where to learn</summary>
        <p className="mt-2">{step.why}</p>
        {step.resources.length > 0 && (
          <p className="mt-2 flex flex-wrap items-center gap-2">
            {step.resources.map((link) => (
              <a key={link} href={link} target="_blank" rel="noopener noreferrer" className="rounded-full border border-line px-3 py-0.5 text-sm no-underline">
                {new URL(link).hostname.replace(/^www\./, '')} ↗
              </a>
            ))}
          </p>
        )}
      </details>
    </li>
  )
}

const TABS = [['path', 'My path'], ['changing', "What's changing"], ['after', 'Where it leads']] as const
type Tab = (typeof TABS)[number][0]

export function RoadmapPage() {
  const { slug = '' } = useParams()
  const { t, lang } = useLang()
  const { user } = useAuth()
  const { slug: mine, choose } = useMyPath()
  const { done, toggle: toggleLocal } = useDoneSteps()
  const [params] = useSearchParams()
  const [roadmap, setRoadmap] = useState<RoadmapDetail | null>(null)
  const [error, setError] = useState('')
  const [tab, setTab] = useState<Tab>('path')
  const [stage, setStage] = useState<number | null>(null)
  const [chosen, setChosen] = useState<CourseDetail | null>(null)
  const area = params.get('area') ?? ''
  const courseSlug = params.get('course') ?? ''

  const load = useCallback(() => {
    api.roadmap(slug, lang).then(setRoadmap).catch((problem: ApiError) => setError(problem.message))
  }, [slug, lang])

  useEffect(load, [load, user])

  // A shorter course fits the same steps into fewer years
  const years = useMemo(() => {
    const grouped = new Map<number, RoadmapStep[]>()
    const last = chosen?.path_years ?? Infinity
    roadmap?.steps.forEach((step) => {
      const year = Math.min(step.year, last)
      grouped.set(year, [...(grouped.get(year) ?? []), step])
    })
    return [...grouped.entries()].sort(([first], [second]) => first - second)
  }, [roadmap, chosen])

  useEffect(() => {
    if (courseSlug) api.course(courseSlug, '').then(setChosen).catch(() => setChosen(null))
    else setChosen(null)
  }, [courseSlug])


  async function toggle(step: RoadmapStep) {
    if (!user) {
      toggleLocal(step.id)
      return
    }
    try {
      await (step.done ? api.unmarkStep(step.id) : api.markStep(step.id))
      load()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  if (error) return <Notice kind="error">{error}</Notice>
  if (!roadmap) return <p className="py-10 text-center text-muted">{t('loading')}</p>

  const isDone = (step: RoadmapStep) => step.done || (!user && done.includes(step.id))
  const doneCount = roadmap.steps.filter(isDone).length
  const nextStep = roadmap.steps.find((step) => !isDone(step))
  const focusYear = Number(params.get('year')) || (nextStep ? Math.min(nextStep.year, chosen?.path_years ?? nextStep.year) : undefined)

  const shownYear = stage ?? focusYear ?? years[0]?.[0]
  const stageSteps = years.find(([year]) => year === shownYear)?.[1] ?? []

  return (
    <div className="mx-auto max-w-4xl">
      {chosen
        ? (
          <p className="text-sm">
            <Link to="/choose">Areas</Link> › <Link to={`/choose/${area}`}>{chosen.field_name}</Link> › <Link to={`/choose/${area}/${chosen.slug}`}>{chosen.name}</Link>
          </p>
        )
        : <p><Link to="/choose">← Choose an area</Link></p>}
      <h1 className="mt-2 text-3xl">{roadmap.name}</h1>
      <p className="mt-2 text-lg text-muted">{roadmap.description}</p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        {mine === roadmap.slug
          ? <Link to="/my-path" className="btn btn-outline">Open My Path</Link>
          : <button type="button" className="btn btn-primary" onClick={() => choose(roadmap.slug, area && courseSlug ? `area=${area}&course=${courseSlug}` : '')}>Make this my path</button>}
        <Link to={`/compare-careers?a=${roadmap.slug}`} className="btn btn-outline">Compare with another career</Link>
        <span className="text-sm text-muted">{doneCount} of {roadmap.step_count} steps done</span>
      </div>

      {chosen?.path_note && <p className="mt-4 rounded-lg bg-pine-soft p-3"><strong>For your course:</strong> {chosen.path_note}</p>}

      <div role="tablist" aria-label="Career sections" className="mt-6 flex gap-1 overflow-x-auto border-b border-line">
        {TABS.map(([value, label]) => (
          <button
            key={value} type="button" role="tab" aria-selected={tab === value} onClick={() => setTab(value)}
            className={`-mb-px cursor-pointer whitespace-nowrap border-b-4 px-3 py-2 font-semibold ${tab === value ? 'border-teal text-pine' : 'border-transparent text-muted'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'path' && (
        <>
          <ol className="mt-5 flex items-center overflow-x-auto pb-2" aria-label="Your journey">
            <li className="whitespace-nowrap rounded-full bg-pine-soft px-3 py-1 text-sm font-semibold text-pine">Start</li>
            {years.map(([year, steps]) => {
              const finished = steps.every(isDone)
              return (
                <li key={year} className="flex items-center">
                  <span aria-hidden="true" className="h-0.5 w-5 bg-line" />
                  <button
                    type="button" aria-current={year === shownYear ? 'step' : undefined} onClick={() => setStage(year)}
                    className={`cursor-pointer whitespace-nowrap rounded-full border-2 px-3 py-1 text-sm font-semibold ${year === shownYear ? 'border-pine bg-pine text-white' : finished ? 'border-[#2e7d32] text-[#2e7d32]' : 'border-teal text-teal'}`}
                  >
                    {finished ? '✓ ' : ''}{t('year')} {year}
                  </button>
                </li>
              )
            })}
            <li className="flex items-center">
              <span aria-hidden="true" className="h-0.5 w-5 bg-line" />
              <button type="button" onClick={() => setTab('after')} className="cursor-pointer whitespace-nowrap rounded-full bg-sun px-3 py-1 text-sm font-semibold text-pine">Your goal →</button>
            </li>
          </ol>

          <h2 className="mt-4 text-2xl">{t('year')} {shownYear}</h2>
          <ul className="mt-3 grid gap-3">
            {stageSteps.map((step) => <Step key={step.id} step={{ ...step, done: isDone(step) }} onToggle={() => toggle(step)} />)}
          </ul>
          <p className="mt-4 text-sm text-muted">This path is general guidance. It has not been checked by someone working in this field yet, so also ask a teacher or senior.</p>
        </>
      )}

      {tab === 'changing' && (
        <>
          <TechChanges roadmap={slug} title="What's changing, and what to learn" />
          <CareerNews roadmap={slug} />
          <EmptyChanges roadmap={slug} />
        </>
      )}

      {tab === 'after' && (
        <>
          <CareerLadder roadmap={slug} />
          <AfterRoadmap roadmap={slug} course={courseSlug} title="Your options" />
          {chosen
            ? <p className="mt-6"><Link to={`/courses/${chosen.slug}`} className="font-semibold">{chosen.name}: see rules and exams →</Link></p>
            : roadmap.courses.length > 0 && (
              <details className="mt-6 rounded-xl border border-line bg-white px-4 py-3">
                <summary className="cursor-pointer font-bold text-pine">Which course leads here?</summary>
                <p className="mt-2 text-sm text-muted">Each course page has its rules and exams.</p>
                <ul className="mt-2 grid gap-1 pb-2">
                  {roadmap.course_slugs.map((course, index) => <li key={course}><Link to={`/courses/${course}`}>{roadmap.courses[index]}</Link></li>)}
                </ul>
              </details>
            )}
        </>
      )}

      <div className="mt-6"><SourceLine record={roadmap} /></div>
      <ReportForm />
    </div>
  )
}

export function MyProgress() {
  const { t, lang } = useLang()
  const [rows, setRows] = useState<Awaited<ReturnType<typeof api.myProgress>> | null>(null)
  const [quiz, setQuiz] = useState<Awaited<ReturnType<typeof api.myQuizResult>>>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.myProgress(lang).then(setRows).catch((problem: ApiError) => setError(problem.message))
    api.myQuizResult(lang).then(setQuiz).catch(() => setQuiz(null))
  }, [lang])

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl">{t('my_progress')}</h1>
      <Notice kind="error">{error}</Notice>
      {quiz && quiz.results.length > 0 && (
        <section className="card mt-4">
          <h2 className="text-xl">{t('last_quiz')}</h2>
          <ul className="mt-2 list-disc pl-5">
            {quiz.results.map((item) => <li key={item.slug}><Link to={`/courses/${item.slug}`}>{item.name}</Link></li>)}
          </ul>
        </section>
      )}
      {rows?.length === 0 && (
        <div className="card mt-4">
          <p>{t('no_progress')}</p>
          <Link to="/roadmaps" className="btn btn-primary mt-3">{t('roadmaps_title')}</Link>
        </div>
      )}
      <ul className="mt-4 grid gap-3">
        {rows?.map((row) => (
          <li key={row.slug} className="card">
            <h2 className="text-lg"><Link to={`/roadmaps/${row.slug}`}>{row.name}</Link></h2>
            <p className="mb-1 text-sm">{row.done} / {row.total} {t('steps_done')}</p>
            <progress max={row.total} value={row.done} className="h-3 w-full accent-teal" />
            <p className="mt-2 text-sm">
              {row.next_step ? <>{t('next_step')}: <strong>{row.next_step}</strong></> : `🎉 ${t('complete')}`}
            </p>
          </li>
        ))}
      </ul>
    </div>
  )
}
