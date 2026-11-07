import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type QuizQuestion, type QuizResult } from '../api/client'
import { Notice } from '../components/Form'
import { useAuth } from '../context/AuthContext'
import { useLang } from '../context/Language'
import { useBackground } from '../context/useBackground'

export const PENDING_QUIZ = 'careerpath-quiz-answers'

function Result({ result, onRetake }: { result: QuizResult; onRetake: () => void }) {
  const { t } = useLang()
  const { user } = useAuth()
  const compare = result.results.map((item) => item.slug).join(',')

  return (
    <>
      <h1 className="text-3xl">{t('result_title')}</h1>
      <p className="mt-3 rounded-lg bg-pine-soft p-3">{t('result_note')}{result.top_tie ? ` ${t('tie_note')}` : ''}</p>
      {result.results.length === 0 && <p className="mt-4 text-muted">{t('no_match')}</p>}
      <ul className="mt-4 grid gap-4">
        {result.results.map((item, index) => (
          <li key={item.slug} className="card">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-xl">{index + 1}. {item.name}</h2>
              <span className="rounded-full bg-sun px-3 py-0.5 text-sm font-bold text-pine">{item.points} / {result.answered} {t('answers_matched')}</span>
            </div>
            <p className="mt-1">{item.summary}</p>
            <h3 className="mt-3">{t('why_suits')}</h3>
            <ul className="list-disc pl-5">{item.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link to={`/courses/${item.slug}`} className="btn btn-primary !min-h-9 !py-1 text-sm">{t('view_details')} →</Link>
              {item.roadmaps.map((road) => (
                <Link key={road.slug} to={`/roadmaps/${road.slug}`} className="btn btn-outline !min-h-9 !py-1 text-sm">{road.name}</Link>
              ))}
            </div>
          </li>
        ))}
      </ul>
      {result.also.length > 0 && (
        <section className="card mt-4">
          <h2 className="text-xl">{t('equally_good')}</h2>
          <ul className="mt-2 flex flex-wrap gap-2">
            {result.also.map((item) => <li key={item.slug}><Link to={`/courses/${item.slug}`}>{item.name}</Link></li>)}
          </ul>
        </section>
      )}
      {!user && result.results.length > 0 && (
        <p className="mt-4 rounded-lg bg-pine-soft p-3">{t('save_result')} <Link to="/register" className="font-semibold">{t('sign_up')}</Link></p>
      )}
      <div className="mt-4 flex flex-wrap gap-2">
        {result.results.length > 1 && <Link to={`/compare?c=${compare}`} className="btn btn-outline">{t('compare_these')}</Link>}
        <button type="button" className="btn btn-outline" onClick={onRetake}>↺ {t('retake')}</button>
      </div>
    </>
  )
}

export function Quiz() {
  const { t, lang } = useLang()
  const background = useBackground()
  const { user } = useAuth()
  const [questions, setQuestions] = useState<QuizQuestion[] | null>(null)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [current, setCurrent] = useState(0)   // 0 is the "what did you study" step
  const [result, setResult] = useState<QuizResult | null>(null)
  const [error, setError] = useState('')
  const heading = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    api.quiz(lang).then(setQuestions).catch((problem: ApiError) => setError(problem.message))
  }, [lang])

  useEffect(() => {
    heading.current?.focus({ preventScroll: true })
  }, [current])

  async function finish(chosen: Record<number, number>) {
    setError('')
    try {
      setResult(await api.scoreQuiz({
        answers: chosen,
        stream_id: background.background.stream_id,
        region_id: background.background.region_id,
        subject_ids: background.background.subject_ids,
      }, lang))
      window.scrollTo(0, 0)
      if (!user) {
        try {
          sessionStorage.setItem(PENDING_QUIZ, JSON.stringify({
            answers: chosen,
            stream_id: background.background.stream_id,
            region_id: background.background.region_id,
            subject_ids: background.background.subject_ids,
          }))
        } catch {
          // Private browsing can block storage. Only the save-after-sign-up step is lost.
        }
      }
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  if (result) {
    return (
      <div className="mx-auto max-w-3xl">
        <Result result={result} onRetake={() => { setResult(null); setAnswers({}); setCurrent(0) }} />
      </div>
    )
  }
  if (!questions) return <p className="py-10 text-center text-muted">{error || t('loading')}</p>

  const total = questions.length + 1
  const question = current > 0 ? questions[current - 1] : null
  const isLast = current === total - 1

  function pick(optionId: number) {
    if (!question) return
    setAnswers({ ...answers, [question.id]: optionId })
    if (!isLast) window.setTimeout(() => setCurrent((step) => step + 1), 180)
  }

  const optionClass = (selected: boolean) =>
    `flex min-h-11 w-full cursor-pointer items-center rounded-lg border px-3 py-2 text-left ${selected ? 'border-teal bg-pine-soft font-semibold' : 'border-line bg-white hover:bg-paper'}`

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-3xl">{t('quiz_title')}</h1>
      <p className="mt-2 text-muted">{t('quiz_help')}</p>
      <div className="mt-4 flex items-center gap-3">
        <progress max={total} value={current + 1} className="h-2 flex-1 accent-teal" aria-hidden="true" />
        <span className="whitespace-nowrap text-sm text-muted">{current + 1} / {total}</span>
      </div>
      <Notice kind="error">{error}</Notice>

      <section className="card mt-4">
        {question ? (
          <>
            <h2 ref={heading} tabIndex={-1} className="mb-3 text-xl outline-none">{question.text}</h2>
            <div className="grid gap-2">
              {question.options.map((option) => (
                <button key={option.id} type="button" aria-pressed={answers[question.id] === option.id} className={optionClass(answers[question.id] === option.id)} onClick={() => pick(option.id)}>
                  {option.text}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            <h2 ref={heading} tabIndex={-1} className="text-xl outline-none">{t('quiz_stream')}</h2>
            <p className="mb-3 text-sm text-muted">{t('quiz_stream_help')}</p>
            <div className="grid gap-2">
              {background.streams.map((stream) => (
                <button
                  key={stream.id} type="button"
                  aria-pressed={background.background.stream_id === stream.id}
                  className={optionClass(background.background.stream_id === stream.id)}
                  onClick={() => { background.choose({ stream_id: stream.id }); window.setTimeout(() => setCurrent(1), 180) }}
                >
                  {stream.name}{stream.aliases.length > 0 ? ` (${stream.aliases.join(', ')})` : ''}
                </button>
              ))}
              <button type="button" className={optionClass(false)} onClick={() => { background.choose({ stream_id: null }); setCurrent(1) }}>{t('not_sure')}</button>
            </div>
          </>
        )}
      </section>

      <div className="mt-4 flex justify-between gap-2">
        {current > 0 ? <button type="button" className="btn btn-outline" onClick={() => setCurrent(current - 1)}>← {t('back')}</button> : <span />}
        {isLast
          ? <button type="button" className="btn btn-primary" onClick={() => finish(answers)}>{t('see_result')} →</button>
          : <button type="button" className="btn btn-primary" onClick={() => setCurrent(current + 1)}>{t('next')} →</button>}
      </div>
    </div>
  )
}
