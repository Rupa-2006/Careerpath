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
      return next
    })
  }, [])

  return { done, toggle }
}
