import { useRef, useState } from 'react'
import type { RoadmapDetail, RoadmapStep, Skill } from '../api/client'
import { exportProgress, importProgress, readStepLog, today, useStepNotes } from '../context/useMyCourse'

const WEEKS = 8
const DAY = 24 * 60 * 60 * 1000

function daysAgo(date: string): number {
  return Math.floor((new Date(`${today()}T00:00:00`).getTime() - new Date(`${date}T00:00:00`).getTime()) / DAY)
}

function nice(date: string): string {
  return new Date(`${date}T00:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

/** Weeks in a row, ending this week or last week, with at least one finished step. */
function weekStreak(dates: string[]): number {
  const weeks = new Set(dates.map((date) => Math.floor(daysAgo(date) / 7)))
  let start = weeks.has(0) ? 0 : weeks.has(1) ? 1 : -1
  if (start < 0) return 0
  let streak = 0
  while (weeks.has(start)) {
    streak += 1
    start += 1
  }
  return streak
}

function Milestone({ reached, icon, title, detail }: { reached: boolean; icon: string; title: string; detail: string }) {
  return (
    <li className={`flex items-center gap-3 rounded-xl border p-3 ${reached ? 'border-[#2e7d32] bg-[#f4fbf5]' : 'border-line bg-white opacity-60'}`}>
      <span aria-hidden="true" className={`text-2xl ${reached ? '' : 'grayscale'}`}>{icon}</span>
      <span>
        <span className="block font-semibold">{reached ? '✓ ' : ''}{title}</span>
        <span className="block text-sm text-muted">{detail}</span>
      </span>
    </li>
  )
}

function ProofNote({ step, note, onSave }: { step: RoadmapStep; note: string; onSave: (text: string) => void }) {
  const [editing, setEditing] = useState(false)
  const [text, setText] = useState(note)
  if (!editing) {
    return note
      ? <p className="mt-1 text-sm">📝 {note} <button type="button" className="cursor-pointer text-teal underline" onClick={() => { setText(note); setEditing(true) }}>Edit</button></p>
      : <button type="button" className="mt-1 cursor-pointer text-sm text-teal underline" onClick={() => setEditing(true)}>+ Add what you made (proof)</button>
  }
  return (
    <form className="mt-2 flex flex-col gap-2 sm:flex-row" onSubmit={(event) => { event.preventDefault(); onSave(text); setEditing(false) }}>
      <label className="sr-only" htmlFor={`proof-${step.id}`}>What you made for {step.title}</label>
      <input
        id={`proof-${step.id}`} className="input flex-1" maxLength={300} value={text} autoFocus
        placeholder="For example: built a budget sheet, or a GitHub link" onChange={(event) => setText(event.target.value)}
      />
      <button type="submit" className="btn btn-primary !min-h-9 !py-1">Save</button>
    </form>
  )
}

/** A student's whole progress on their path, built only from what they ticked in this browser. */
export function ProgressTracker({ roadmap, done, skills, have }: { roadmap: RoadmapDetail; done: number[]; skills: Skill[]; have: string[] }) {
  const { notes, save } = useStepNotes()
  const [message, setMessage] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)
  const log = readStepLog()

  const isDone = (step: RoadmapStep) => step.done || done.includes(step.id)
  const finished = roadmap.steps.filter(isDone)
  const stepPercent = roadmap.steps.length ? Math.round((finished.length * 100) / roadmap.steps.length) : 0
  const skillsHave = skills.filter((skill) => have.includes(skill.slug)).length
  const skillPercent = skills.length ? Math.round((skillsHave * 100) / skills.length) : 0
  // Steps are the main plan; skills show what the student can already do. Both count.
  const readiness = skills.length ? Math.round(stepPercent * 0.7 + skillPercent * 0.3) : stepPercent

  const years = [...new Set(roadmap.steps.map((step) => step.year))].sort((a, b) => a - b)
  const byYear = years.map((year) => {
    const steps = roadmap.steps.filter((step) => step.year === year)
    return { year, total: steps.length, done: steps.filter(isDone).length }
  })
  const firstOpenYear = byYear.find((item) => item.done < item.total)?.year

  const dates = finished.map((step) => log[step.id]).filter((date): date is string => Boolean(date))
  const weeks = Array.from({ length: WEEKS }, (_, index) => dates.filter((date) => Math.floor(daysAgo(date) / 7) === WEEKS - 1 - index).length)
  const most = Math.max(1, ...weeks)
  const streak = weekStreak(dates)
  const last = [...dates].sort().at(-1)
  const proofs = finished.filter((step) => notes[step.id]).length

  function download() {
    const blob = new Blob([exportProgress()], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `careerpath-progress-${today()}.json`
    link.click()
    URL.revokeObjectURL(link.href)
    setMessage('Saved. Keep this file to open your progress on another phone or computer.')
  }

  async function load(file: File | undefined) {
    if (!file) return
    if (importProgress(await file.text())) {
      window.location.reload()
    } else {
      setMessage("That file isn't a PathMithra progress file.")
    }
  }

  return (
    <section className="mt-6" aria-labelledby="progress-title">
      <h2 id="progress-title" className="text-2xl">My progress</h2>

      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        <div className="card text-center">
          <p className="text-4xl font-bold text-pine">{readiness}%</p>
          <p className="mt-1 font-semibold">Path readiness</p>
          <p className="text-xs text-muted">Steps count 70%, skills 30%</p>
        </div>
        <div className="card text-center">
          <p className="text-4xl font-bold text-pine">{finished.length}<span className="text-xl text-muted">/{roadmap.steps.length}</span></p>
          <p className="mt-1 font-semibold">Steps finished</p>
          <p className="text-xs text-muted">{proofs} with proof of work</p>
        </div>
        <div className="card text-center">
          <p className="text-4xl font-bold text-pine">{skillsHave}<span className="text-xl text-muted">/{skills.length}</span></p>
          <p className="mt-1 font-semibold">Skills you can do</p>
          <p className="text-xs text-muted">{streak > 0 ? `🔥 ${streak} week${streak > 1 ? 's' : ''} in a row` : last ? `Last step: ${nice(last)}` : 'Tick a step to start'}</p>
        </div>
      </div>

      <div className="card mt-3">
        <h3 className="font-semibold">Year by year</h3>
        <ul className="mt-2 grid gap-2">
          {byYear.map((item) => (
            <li key={item.year} className="grid grid-cols-[4.5rem_1fr_3.5rem] items-center gap-3 text-sm">
              <span className={item.year === firstOpenYear ? 'font-bold text-pine' : ''}>Year {item.year}</span>
              <span className="h-3 overflow-hidden rounded-full bg-pine-soft">
                <span className="block h-full rounded-full bg-teal" style={{ width: `${(item.done * 100) / item.total}%` }} />
              </span>
              <span className="text-right text-muted">{item.done}/{item.total}</span>
            </li>
          ))}
        </ul>
        {firstOpenYear && <p className="mt-2 text-sm">You're working on <strong>Year {firstOpenYear}</strong>.</p>}
      </div>

      <div className="card mt-3">
        <h3 className="font-semibold">Steps finished in the last {WEEKS} weeks</h3>
        <div className="mt-3 flex h-20 items-end gap-2" role="img" aria-label={`Steps finished each week: ${weeks.join(', ')}`}>
          {weeks.map((count, index) => (
            <div key={index} className="flex flex-1 flex-col items-center gap-1">
              <span className="text-xs text-muted">{count || ''}</span>
              <span className={`w-full rounded-t ${count ? 'bg-teal' : 'bg-pine-soft'}`} style={{ height: `${count ? Math.max(12, (count * 56) / most) : 4}px` }} />
            </div>
          ))}
        </div>
        <p className="mt-1 flex justify-between text-xs text-muted"><span>{WEEKS} weeks ago</span><span>This week</span></p>
      </div>

      <h3 className="mt-6 text-xl">Milestones</h3>
      <ul className="mt-2 grid gap-2 sm:grid-cols-2">
        <Milestone reached={finished.length >= 1} icon="🚀" title="First step" detail="Finish any step on your path." />
        <Milestone reached={byYear.some((item) => item.done === item.total)} icon="📅" title="A full year done" detail="Finish every step in one year." />
        <Milestone reached={stepPercent >= 50} icon="⛰️" title="Halfway there" detail="Finish half of your path." />
        <Milestone reached={proofs >= 3} icon="🛠️" title="Builder" detail="Add proof of work to 3 steps." />
        <Milestone reached={skills.length > 0 && skillPercent >= 50} icon="🧠" title="Skilled up" detail="Tick half of the skills for your career." />
        <Milestone reached={finished.length > 0 && finished.length === roadmap.steps.length} icon="🎓" title="Path complete" detail="Finish every step." />
      </ul>

      {finished.length > 0 && (
        <>
          <h3 className="mt-6 text-xl">What I've done</h3>
          <p className="text-sm text-muted">Add what you made for each step. This becomes a list you can use in your resume.</p>
          <ol className="mt-2 grid gap-2">
            {finished.map((step) => (
              <li key={step.id} className="card !p-3">
                <p className="font-semibold">✓ {step.title} <span className="font-normal text-muted">· Year {step.year}{log[step.id] ? ` · ${nice(log[step.id])}` : ''}</span></p>
                <ProofNote step={step} note={notes[step.id] ?? ''} onSave={(text) => save(step.id, text)} />
              </li>
            ))}
          </ol>
        </>
      )}

      <div className="card mt-6 print:hidden">
        <h3 className="font-semibold">Keep your progress safe</h3>
        <p className="mt-1 text-sm">Your progress is saved only on this device. Download it as a file to keep it, or to open it on another phone or computer.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className="btn btn-primary" onClick={download}>Download my progress</button>
          <button type="button" className="btn btn-outline" onClick={() => fileInput.current?.click()}>Open a progress file</button>
          <button type="button" className="btn btn-outline" onClick={() => window.print()}>Print or save as PDF</button>
          <input ref={fileInput} type="file" accept="application/json,.json" className="hidden" onChange={(event) => load(event.target.files?.[0])} />
        </div>
        {message && <p className="mt-2 text-sm" role="status">{message}</p>}
      </div>
    </section>
  )
}
