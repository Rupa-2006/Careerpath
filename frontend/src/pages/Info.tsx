import { useEffect, useState } from 'react'
import { api, type ApiError, type Dates, type OpportunitySource, type Updates } from '../api/client'
import { Notice } from '../components/Form'
import { DateCard, ReportForm } from '../components/Journey'
import { TechChanges } from '../components/TechChanges'
import { useLang } from '../context/Language'
import { useBackground } from '../context/useBackground'

export function DatesPage() {
  const { t, lang } = useLang()
  const { streams } = useBackground()
  const [stream, setStream] = useState<number | null>(null)
  const [dates, setDates] = useState<Dates | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.dates(lang, stream).then(setDates).catch((problem: ApiError) => setError(problem.message))
  }, [lang, stream])

  const empty = dates && dates.upcoming.length === 0 && dates.waiting.length === 0

  return (
    <>
      <h1 className="text-3xl">{t('dates_title')}</h1>
      <p className="mt-2 max-w-2xl text-muted">{t('dates_help')}</p>
      <div className="mt-4 max-w-sm">
        <select className="input" aria-label={t('quiz_stream')} value={stream ?? ''} onChange={(event) => setStream(Number(event.target.value) || null)}>
          <option value="">{t('all_groups')}</option>
          {streams.filter((item) => item.subjects.length > 0).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </div>
      <Notice kind="error">{error}</Notice>
      {empty && <p className="mt-4 text-muted">{t('dates_empty')}</p>}
      {dates && dates.upcoming.length > 0 && (
        <>
          <h2 className="mt-6 text-2xl">{t('dates_upcoming')}</h2>
          <ul className="mt-3 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{dates.upcoming.map((item) => <DateCard key={item.id} item={item} />)}</ul>
        </>
      )}
      {dates && dates.waiting.length > 0 && (
        <>
          <h2 className="mt-6 text-2xl">{t('dates_waiting')}</h2>
          <ul className="mt-3 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{dates.waiting.map((item) => <DateCard key={item.id} item={item} />)}</ul>
        </>
      )}
      <ReportForm />
    </>
  )
}

export function UpdatesPage() {
  const { t, lang } = useLang()
  const [updates, setUpdates] = useState<Updates | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.updates(lang).then(setUpdates).catch((problem: ApiError) => setError(problem.message))
  }, [lang])

  return (
    <>
      <h1 className="text-3xl">{t('updates_title')}</h1>
      <Notice kind="error">{error}</Notice>
      <TechChanges title="What's changing, and what to learn" />
      <h2 className="mt-6 text-2xl">{t('tools')}</h2>
      <ul className="mt-3 grid gap-4 md:grid-cols-2">
        {updates?.tools.map((item) => (
          <li key={item.link} className="card">
            <h3 className="text-lg">{item.title}</h3>
            <p className="text-sm text-muted">{item.source_name}</p>
            <p className="mt-1"><strong>{t('why_matters')}:</strong> {item.why_it_matters}</p>
            <a href={item.link} target="_blank" rel="noopener noreferrer" className="mt-1 inline-block font-semibold">{t('open_link')} ↗</a>
          </li>
        ))}
      </ul>
      {updates && updates.latest.length > 0 && (
        <>
          <h2 className="mt-8 text-2xl">{t('latest')}</h2>
          <p className="mt-1 text-sm text-muted">{t('news_note')}</p>
          {updates.last_collected && <p className="text-sm text-muted">{t('collected')}: {updates.last_collected.slice(0, 10)}</p>}
          <ul className="mt-3 grid gap-2">
            {updates.latest.map((item) => (
              <li key={item.link} className="rounded-lg border border-line bg-white p-3">
                <a href={item.link} target="_blank" rel="noopener noreferrer">{item.title}</a>
                <p className="text-sm text-muted">{item.source_name}{item.published_at ? ` · ${item.published_at.slice(0, 10)}` : ''}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  )
}

export function OpportunitiesPage() {
  const { t, lang } = useLang()
  const [sources, setSources] = useState<OpportunitySource[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.opportunitySources(lang).then(setSources).catch((problem: ApiError) => setError(problem.message))
  }, [lang])

  return (
    <>
      <h1 className="text-3xl">{t('jobs_title')}</h1>
      <p className="mt-3 max-w-3xl rounded-lg bg-pine-soft p-3">{t('jobs_note')}</p>
      <Notice kind="error">{error}</Notice>
      <ul className="mt-4 grid gap-4 md:grid-cols-2">
        {sources.map((item) => (
          <li key={item.url} className="card">
            <h2 className="text-lg">{item.name}</h2>
            <p className="mt-1">{item.description}</p>
            <a href={item.url} target="_blank" rel="noopener noreferrer" className="mt-1 inline-block font-semibold">{new URL(item.url).hostname.replace(/^www\./, '')} ↗</a>
          </li>
        ))}
      </ul>
    </>
  )
}
