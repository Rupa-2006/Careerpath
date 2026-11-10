import { useCallback, useEffect, useState } from 'react'
import type { DiaryEntry, SavedProgress } from '../api/client'

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
  schedulePush()
}

// ---- Keeping a logged-in student's progress in their account.
// The browser stays the working copy, so every page works the same with or without login.
const CHANGED = 'careerpath-progress-changed'
let push: ((data: SavedProgress) => Promise<unknown>) | null = null
let timer: ReturnType<typeof setTimeout> | undefined

function schedulePush() {
  if (!push) return
  clearTimeout(timer)
  timer = setTimeout(() => {
    push?.(collectLocal()).catch(() => {
      // Offline or a server problem: the next change tries again, and nothing is lost on this device.
    })
  }, 800)
}

/** Called by the login state: a function to save to the account, or null when logged out. */
export function setAccountSync(save: ((data: SavedProgress) => Promise<unknown>) | null) {
  push = save
  if (!save) clearTimeout(timer)
}

// A logged-in student's career was chosen at sign-up and stays fixed.
let fixedPath = ''

/** Called by the login state with the account's career, or '' when logged out. */
export function setFixedPath(path: string) {
  fixedPath = path
  window.dispatchEvent(new Event(CHANGED))
}

/** Lets every hook on the page re-read storage after the account's progress arrives. */
function useOnProgressChange(reload: () => void) {
  useEffect(() => {
    window.addEventListener(CHANGED, reload)
    return () => window.removeEventListener(CHANGED, reload)
  }, [reload])
}

/** The chosen career stays in this browser, so a student needs no account and shares no personal details. */
export function useMyPath() {
  const [slug, setSlug] = useState(() => read(PATH_KEY))
  const [from, setFrom] = useState(() => read(FROM_KEY))
  const [fixed, setFixed] = useState(() => Boolean(fixedPath))
  useOnProgressChange(useCallback(() => {
    setSlug(read(PATH_KEY))
    setFrom(read(FROM_KEY))
    setFixed(Boolean(fixedPath))
  }, []))

  const choose = useCallback((next: string, chosenFrom = '') => {
    if (fixedPath) return   // an account's career can't be changed here
    setSlug(next)
    setFrom(chosenFrom)
    write(PATH_KEY, next)
    write(FROM_KEY, chosenFrom)
  }, [])

  return { slug, from, choose, fixed }
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
  useOnProgressChange(useCallback(() => setDone(savedSteps()), []))

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
const DIARY_KEY = 'careerpath-diary'       // the student's private learning diary
const ALL_KEYS = [PATH_KEY, FROM_KEY, STEPS_KEY, LOG_KEY, NOTES_KEY, SKILLS_KEY, DIARY_KEY]

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
  useOnProgressChange(useCallback(() => setNotes(readObject(NOTES_KEY)), []))
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

function savedDiary(): DiaryEntry[] {
  try {
    const value = JSON.parse(read(DIARY_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

/** Newest first: by the day it is about, then by when it was written. */
function byNewest(a: DiaryEntry, b: DiaryEntry) {
  return b.on.localeCompare(a.on) || b.at.localeCompare(a.at)
}

/** The learning diary: what the student did, learned and will do next. */
export function useDiary() {
  const [all, setAll] = useState<DiaryEntry[]>(savedDiary)
  useOnProgressChange(useCallback(() => setAll(savedDiary()), []))

  const keep = useCallback((change: (current: DiaryEntry[]) => DiaryEntry[]) => {
    setAll((current) => {
      const next = change(current)
      write(DIARY_KEY, next.length ? JSON.stringify(next) : '')
      return next
    })
  }, [])

  const save = useCallback((entry: Omit<DiaryEntry, 'id' | 'at'> & { id?: string }) => {
    const id = entry.id ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
    const clean = {
      ...entry, id, at: new Date().toISOString(),
      did: entry.did.trim().slice(0, 500), learned: entry.learned.trim().slice(0, 500), next: entry.next.trim().slice(0, 500),
    }
    keep((current) => [...current.filter((item) => item.id !== id), clean])
  }, [keep])

  const remove = useCallback((id: string) => {
    keep((current) => current.map((item) => item.id === id
      ? { id, on: item.on, at: new Date().toISOString(), did: '', learned: '', next: '', step: null, deleted: true }
      : item))
  }, [keep])

  const entries = all.filter((item) => !item.deleted).sort(byNewest)
  return { entries, save, remove }
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
  useOnProgressChange(useCallback(() => setHave(savedSkills()), []))
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

// ---- Moving progress between this device and an account

export function collectLocal(): SavedProgress {
  const log = readStepLog()
  const notes = readObject(NOTES_KEY)
  const steps: SavedProgress['steps'] = {}
  for (const id of savedSteps()) {
    const entry: { on?: string; note?: string } = {}
    if (log[id]) entry.on = log[id]
    if (notes[id]) entry.note = notes[id]
    steps[String(id)] = entry
  }
  return { path: read(PATH_KEY), path_from: read(FROM_KEY), steps, skills: savedSkills(), diary: savedDiary() }
}

function applyLocal(data: SavedProgress) {
  const ids = Object.keys(data.steps).map(Number).filter(Number.isFinite)
  const log: Record<string, string> = {}
  const notes: Record<string, string> = {}
  for (const [id, entry] of Object.entries(data.steps)) {
    if (entry.on) log[id] = entry.on
    if (entry.note) notes[id] = entry.note
  }
  const saving = push
  push = null   // writing the account's own data back here must not send it straight back
  write(PATH_KEY, data.path)
  write(FROM_KEY, data.path_from)
  write(STEPS_KEY, ids.length ? JSON.stringify(ids) : '')
  write(LOG_KEY, Object.keys(log).length ? JSON.stringify(log) : '')
  write(NOTES_KEY, Object.keys(notes).length ? JSON.stringify(notes) : '')
  write(SKILLS_KEY, data.skills.length ? JSON.stringify(data.skills) : '')
  write(DIARY_KEY, data.diary?.length ? JSON.stringify(data.diary) : '')
  push = saving
  window.dispatchEvent(new Event(CHANGED))
}

/** Account and device together: nothing ticked on either side is lost. The account's chosen career wins. */
export function mergeProgress(account: SavedProgress, device: SavedProgress): SavedProgress {
  const steps: SavedProgress['steps'] = { ...device.steps }
  for (const [id, entry] of Object.entries(account.steps)) {
    const local = steps[id] ?? {}
    const on = [entry.on, local.on].filter(Boolean).sort()[0]
    const note = entry.note || local.note
    steps[id] = { ...(on ? { on } : {}), ...(note ? { note } : {}) }
  }
  return {
    path: account.path || device.path,
    path_from: account.path ? account.path_from : device.path_from,
    steps,
    skills: [...new Set([...account.skills, ...device.skills])].sort(),
    diary: mergeDiary(account.diary ?? [], device.diary ?? []),
  }
}

/** After login: combine both copies, then keep the result here and in the account. */
export async function joinAccount(load: () => Promise<SavedProgress>, save: (data: SavedProgress) => Promise<unknown>) {
  const merged = mergeProgress(await load(), collectLocal())
  applyLocal(merged)
  await save(merged)
}

/** After logout the next person on this computer must not see the student's progress. */
export function clearLocalProgress() {
  setAccountSync(null)
  for (const key of ALL_KEYS) write(key, '')
  window.dispatchEvent(new Event(CHANGED))
}

/** "Doctor (MBBS)" reads better in a sentence as "Doctor". */
export function shortName(name: string): string {
  return name.replace(/\s*\(.*\)\s*$/, '')
}

/** Each entry once; when both copies have it, the most recently edited one wins (a deletion counts as an edit). */
function mergeDiary(account: DiaryEntry[], device: DiaryEntry[]): DiaryEntry[] {
  const merged = new Map<string, DiaryEntry>()
  for (const entry of [...account, ...device]) {
    const other = merged.get(entry.id)
    if (!other || entry.at > other.at) merged.set(entry.id, entry)
  }
  return [...merged.values()]
}
