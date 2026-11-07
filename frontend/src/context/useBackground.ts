import { useEffect, useMemo, useState } from 'react'
import { api, type ApiError, type Region, type Stream, type Subject } from '../api/client'
import { useAuth } from './AuthContext'
import { useLang } from './Language'

const STORAGE_KEY = 'careerpath-background'

export type Background = { region_id: number | null; stream_id: number | null; subject_ids: number[] }

function saved(): Background {
  try {
    return { region_id: null, stream_id: null, subject_ids: [], ...JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}') }
  } catch {
    return { region_id: null, stream_id: null, subject_ids: [] }
  }
}

/** The student's State, stream and subjects, shared by every page that checks eligibility. */
export function useBackground() {
  const { user, setUser } = useAuth()
  const { lang } = useLang()
  const [regions, setRegions] = useState<Region[]>([])
  const [streams, setStreams] = useState<Stream[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [local, setLocal] = useState<Background>(saved)
  const [error, setError] = useState('')
  const [savedToAccount, setSavedToAccount] = useState(false)

  useEffect(() => {
    Promise.all([api.states(), api.streams(), api.subjects()])
      .then(([loadedRegions, loadedStreams, loadedSubjects]) => {
        setRegions(loadedRegions)
        setStreams(loadedStreams)
        setSubjects(loadedSubjects)
      })
      .catch((problem: ApiError) => setError(problem.message))
  }, [])

  // A logged-in student's account decides State and stream; exact subjects stay on this device
  const background: Background = useMemo(
    () => (user ? { ...local, region_id: user.region_id, stream_id: user.stream_id } : local),
    [user, local],
  )

  async function choose(change: Partial<Background>) {
    const next = { ...background, ...change }
    setLocal(next)
    setSavedToAccount(false)
    setError('')
    try {
      const stored = user ? { ...next, region_id: null, stream_id: null } : next
      localStorage.setItem(STORAGE_KEY, JSON.stringify(stored))
    } catch {
      // Private browsing can block storage. The choice still works on this page.
    }
    if (user && ('region_id' in change || 'stream_id' in change)) {
      const { region_id, stream_id } = next
      try {
        setUser(await api.updateProfile({ region_id, stream_id }))
        setSavedToAccount(true)
      } catch (problem) {
        setError((problem as ApiError).message)
      }
    }
  }

  const query = useMemo(() => {
    const params = new URLSearchParams({ lang })
    if (background.region_id) params.set('region', String(background.region_id))
    if (background.stream_id) params.set('stream', String(background.stream_id))
    if (background.subject_ids.length) params.set('subjects', background.subject_ids.join(','))
    return params.toString()
  }, [background, lang])

  return { background, choose, query, regions, streams, subjects, error, savedToAccount, loggedIn: Boolean(user) }
}
