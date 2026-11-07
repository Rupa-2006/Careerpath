import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type AssistantCard, type AssistantReply } from '../api/client'
import { BackgroundForm } from '../components/BackgroundForm'
import { Notice } from '../components/Form'
import { EligibilityBadge, SourceLine, TrustBadge } from '../components/Trust'
import { useLang } from '../context/Language'
import { useBackground } from '../context/useBackground'

type Turn = { id: number; question: string; reply: AssistantReply | null }

const STARTERS = ['What can I do after Class 12?', 'I like coding', 'What is JEE Main?', 'BCA vs B.Sc Computer Science']

function Card({ card }: { card: AssistantCard }) {
  const { t } = useLang()
  return (
    <li className="card flex flex-col gap-1">
      <div className="flex flex-wrap gap-1">
        {card.eligibility && <EligibilityBadge eligibility={card.eligibility} />}
        <TrustBadge status={card.status} />
      </div>
      <h3 className="text-lg">{card.to ? <Link to={card.to} className="text-pine">{card.title}</Link> : card.title}</h3>
      <p className="text-sm"><strong>{t('as_why')}:</strong> {card.why}</p>
      <p className="text-sm text-muted">{card.detail}</p>
      {card.eligibility && card.eligibility.missing.length > 0 && <p className="text-sm">Needs: {card.eligibility.missing.join('; ')}</p>}
      <SourceLine record={card} />
    </li>
  )
}

export function Assistant() {
  const { t, lang } = useLang()
  const state = useBackground()
  const { background } = state
  const [turns, setTurns] = useState<Turn[]>([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const busy = turns.some((turn) => turn.reply === null)
  const end = useRef<HTMLDivElement>(null)
  const nextId = useRef(1)

  useEffect(() => {
    if (turns.length) end.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [turns])

  async function ask(question: string) {
    const message = question.trim()
    if (!message || busy) return
    const id = nextId.current++
    setError('')
    setDraft('')
    setTurns((current) => [...current, { id, question: message, reply: null }])
    try {
      const reply = await api.askAssistant({ message, lang, ...background })
      setTurns((current) => current.map((turn) => (turn.id === id ? { ...turn, reply } : turn)))
    } catch (problem) {
      setTurns((current) => current.filter((turn) => turn.id !== id))
      setDraft(message)
      setError((problem as ApiError).message)
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void ask(draft)
  }

  const last = turns.at(-1)?.reply
  const suggestions = last ? last.next_questions : STARTERS

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-3xl">{t('as_title')}</h1>
      <p className="mt-2">{t('as_help')}</p>
      <p className="mt-3 rounded-lg bg-pine-soft p-3 text-sm">{t('as_trust')}</p>

      <details className="mt-4" open={!background.stream_id && background.subject_ids.length === 0}>
        <summary className="cursor-pointer font-semibold text-teal">{t('as_background')}</summary>
        <div className="mt-2"><BackgroundForm state={state} /></div>
      </details>

      <div className="mt-4 grid gap-4" role="log" aria-live="polite">
        {turns.map((turn) => (
          <section key={turn.id} className="grid gap-2">
            <p className="ml-auto max-w-[85%] rounded-lg bg-pine p-3 text-white">
              <span className="sr-only">{t('as_you')}: </span>{turn.question}
            </p>
            {turn.reply === null
              ? <p className="text-muted">{t('as_thinking')}</p>
              : (
                <div className="grid gap-2">
                  <p className="rounded-lg border border-line bg-paper p-3">
                    <span className="sr-only">{t('as_bot')}: </span>{turn.reply.text}
                  </p>
                  {turn.reply.used_ai && <p className="text-xs text-muted">{t('as_ai')}</p>}
                  {turn.reply.cards.length > 0 && (
                    <ul className="grid gap-3 sm:grid-cols-2">
                      {turn.reply.cards.map((card) => <Card key={`${card.kind}-${card.title}`} card={card} />)}
                    </ul>
                  )}
                </div>
              )}
          </section>
        ))}
        <div ref={end} />
      </div>

      {suggestions.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {suggestions.map((question) => (
            <button key={question} type="button" disabled={busy} onClick={() => void ask(question)} className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm">
              {question}
            </button>
          ))}
        </div>
      )}
      <Notice kind="error">{error}</Notice>
      <form onSubmit={submit} className="mt-3 flex flex-wrap gap-2">
        <label className="sr-only" htmlFor="assistant-question">{t('as_label')}</label>
        <input
          id="assistant-question" className="input flex-1 basis-56" maxLength={500} value={draft} autoComplete="off"
          placeholder={t('as_placeholder')} onChange={(event) => setDraft(event.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={busy || !draft.trim()}>{t('as_send')}</button>
      </form>
    </div>
  )
}
