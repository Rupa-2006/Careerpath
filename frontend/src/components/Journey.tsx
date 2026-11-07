import { useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { api, type ApiError, type ImportantDate } from '../api/client'
import { useLang } from '../context/Language'
import { Notice } from './Form'

const CERTAINTY_COLOURS: Record<ImportantDate['certainty'], string> = {
  CONFIRMED: 'bg-[#e3f4e5] text-[#1f5c23]',
  REPORTED: 'bg-[#fff1d6] text-[#7a4d00]',
  NOT_ANNOUNCED: 'bg-[#eceff3] text-[#47525f]',
}

export function DateCard({ item }: { item: ImportantDate }) {
  const { t, lang } = useLang()
  const format = (value: string) =>
    new Date(`${value}T00:00:00`).toLocaleDateString(lang === 'te' ? 'te-IN' : 'en-IN', { day: 'numeric', month: 'short', year: 'numeric' })

  return (
    <li className="card flex flex-col gap-1">
      <h3 className="text-lg">{item.title}</h3>
      {item.starts_on && (
        <p>
          <strong className="text-teal">{format(item.starts_on)}{item.ends_on ? ` – ${format(item.ends_on)}` : ''}</strong>{' '}
          <span className="text-sm font-semibold text-danger">
            {item.days_left! > 0 ? `${item.days_left} ${t('days_left')}` : item.days_left === 0 ? t('today') : t('happening_now')}
          </span>
        </p>
      )}
      <span className={`self-start rounded px-2 py-0.5 text-xs font-semibold ${CERTAINTY_COLOURS[item.certainty]}`}>{t(item.certainty)}</span>
      {item.note && <p className="text-sm">{item.note}</p>}
      {item.recheck_due && <p className="text-sm font-semibold text-danger">{t('recheck')}</p>}
      <p className="text-sm text-muted">
        {item.source && <a href={item.source.url} target="_blank" rel="noopener noreferrer">{t('official_site')} ↗</a>}
        {' · '}{t('checked')}: {format(item.checked_on)}
      </p>
    </li>
  )
}

export function ReportForm() {
  const { t } = useLang()
  const location = useLocation()
  const [message, setMessage] = useState('')
  const [website, setWebsite] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    try {
      await api.report(location.pathname.slice(0, 200), message, website)
      setSent(true)
      setMessage('')
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  return (
    <details className="mt-8">
      <summary className="min-h-11 cursor-pointer py-2 font-semibold text-teal">{t('report_title')}</summary>
      <form onSubmit={submit} className="mt-2 max-w-xl">
        <Notice kind="error">{error}</Notice>
        {sent && <Notice kind="success">{t('report_thanks')}</Notice>}
        <p className="mb-2 text-sm text-muted">{t('report_help')}</p>
        <label className="absolute -left-[9999px]" aria-hidden="true">
          Website <input type="text" tabIndex={-1} autoComplete="off" value={website} onChange={(event) => setWebsite(event.target.value)} />
        </label>
        <textarea className="input" required minLength={3} maxLength={1000} rows={3} aria-label={t('report_title')} value={message} onChange={(event) => setMessage(event.target.value)} />
        <button type="submit" className="btn btn-primary mt-2">{t('report_send')}</button>
      </form>
    </details>
  )
}
