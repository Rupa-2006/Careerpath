import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, type User } from '../api/client'
import { clearLocalProgress, joinAccount, setAccountSync } from './useMyCourse'

type Auth = {
  user: User | null
  loading: boolean
  setUser: (user: User | null) => void
  logout: () => Promise<void>
}

const AuthContext = createContext<Auth | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false))
  }, [])

  // A logged-in student's My Path follows them: join this device's progress with the account, then keep saving.
  useEffect(() => {
    if (!user) {
      setAccountSync(null)
      return
    }
    let active = true
    const keepSaving = () => { if (active) setAccountSync(api.saveProgress) }
    joinAccount(api.savedProgress, api.saveProgress).then(keepSaving, keepSaving)
    return () => { active = false }
  }, [user])

  const value = useMemo(() => ({
    user,
    loading,
    setUser,
    logout: async () => {
      await api.logout()
      clearLocalProgress()
      setUser(null)
    },
  }), [user, loading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth must be used inside AuthProvider')
  return auth
}
