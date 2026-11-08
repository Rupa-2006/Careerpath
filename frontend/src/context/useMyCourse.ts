import { useCallback, useState } from 'react'

const PATH_KEY = 'careerpath-my-path'
const FROM_KEY = 'careerpath-my-path-from'
const STEPS_KEY = 'careerpath-done-steps'

function read(key: string): string {
  try {
    return localStorage.getItem(key) ?? ''
  } catch {
    return ''
  }
}

function write(key: string, value: string) {
  try {
    if (value) localStorage.setItem(key, value)
    else localStorage.removeItem(key)
  } catch {
    // Private browsing can block storage. The choice still works until the page closes.
  }
}

/** The chosen career stays in this browser, so a student needs no account and shares no personal details. */
export function useMyPath() {
  const [slug, setSlug] = useState(() => read(PATH_KEY))
  const [from, setFrom] = useState(() => read(FROM_KEY))

  const choose = useCallback((next: string, chosenFrom = '') => {
    setSlug(next)
    setFrom(chosenFrom)
    write(PATH_KEY, next)
    write(FROM_KEY, chosenFrom)
  }, [])

  return { slug, from, choose }
}

function savedSteps(): number[] {
  try {
    const value = JSON.parse(read(STEPS_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

/** Finished roadmap steps for students without an account. */
export function useDoneSteps() {
  const [done, setDone] = useState<number[]>(savedSteps)

  const toggle = useCallback((id: number) => {
    setDone((current) => {
      const next = current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
      write(STEPS_KEY, JSON.stringify(next))
      logStep(id, next.includes(id))
      return next
    })
  }, [])

  return { done, toggle }
}

// ---- Progress tracking. Everything stays in this browser; a student can download it as a file to move devices.
const LOG_KEY = 'careerpath-step-log'      // step id -> date it was finished (YYYY-MM-DD)
const NOTES_KEY = 'careerpath-step-notes'  // step id -> what the student made, as proof
const SKILLS_KEY = 'careerpath-my-skills'
const ALL_KEYS = [PATH_KEY, FROM_KEY, STEPS_KEY, LOG_KEY, NOTES_KEY, SKILLS_KEY]

function readObject(key: string): Record<string, string> {
  try {
    const value = JSON.parse(read(key) || '{}')
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
  } catch {
    return {}
  }
}

export function today(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

/** When each step was finished, so the student can see their activity over time. */
export function readStepLog(): Record<string, string> {
  return readObject(LOG_KEY)
}

export function logStep(id: number, finished: boolean) {
  const log = readObject(LOG_KEY)
  if (finished) log[id] = log[id] ?? today()
  else delete log[id]
  write(LOG_KEY, JSON.stringify(log))
}

/** A short note on what the student made for a step: their proof of work. */
export function useStepNotes() {
  const [notes, setNotes] = useState<Record<string, string>>(() => readObject(NOTES_KEY))
  const save = useCallback((id: number, text: string) => {
    setNotes((current) => {
      const next = { ...current }
      if (text.trim()) next[id] = text.trim().slice(0, 300)
      else delete next[id]
      write(NOTES_KEY, JSON.stringify(next))
      return next
    })
  }, [])
  return { notes, save }
}

function savedSkills(): string[] {
  try {
    const value = JSON.parse(read(SKILLS_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

/** Skills the student says they can already do. Shared by the Skills page, the skill gap and the tracker. */
export function useMySkills() {
  const [have, setHave] = useState<string[]>(savedSkills)
  const toggle = useCallback((slug: string) => {
    setHave((current) => {
      const next = current.includes(slug) ? current.filter((item) => item !== slug) : [...current, slug]
      write(SKILLS_KEY, JSON.stringify(next))
      return next
    })
  }, [])
  return { have, toggle }
}

/** Everything the student saved, as one file they can keep or open on another device. */
export function exportProgress(): string {
  const data: Record<string, string> = {}
  for (const key of ALL_KEYS) {
    const value = read(key)
    if (value) data[key] = value
  }
  return JSON.stringify({ app: 'CareerPath', version: 1, saved_on: today(), data }, null, 2)
}

/** Only CareerPath's own keys are accepted, and only as text, so a strange file can't change anything else. */
export function importProgress(text: string): boolean {
  try {
    const file = JSON.parse(text)
    if (file?.app !== 'CareerPath' || typeof file.data !== 'object' || file.data === null) return false
    for (const key of ALL_KEYS) {
      const value = file.data[key]
      if (typeof value === 'string' && value.length < 100_000) write(key, value)
    }
    return true
  } catch {
    return false
  }
}
