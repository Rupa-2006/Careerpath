import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api, type ApiError, type RoadmapSummary } from '../api/client'
import { useMyPath } from '../context/useMyCourse'
import { Field, Notice } from '../components/Form'
import { useAuth } from '../context/AuthContext'
import { PENDING_QUIZ } from './Quiz'

/** A student who took the quiz before logging in keeps their result in their account. */
async function savePendingQuiz() {
  try {
    const pending = sessionStorage.getItem(PENDING_QUIZ)
    if (pending) {
      sessionStorage.removeItem(PENDING_QUIZ)
      await api.scoreQuiz(JSON.parse(pending), 'en')
    }
  } catch {
    // Losing a saved quiz result must never stop someone logging in.
  }
}

function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const { slug: pathOnDevice } = useMyPath()
  const [path, setPath] = useState(pathOnDevice)
  const [careers, setCareers] = useState<RoadmapSummary[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const isLogin = mode === 'login'

  useEffect(() => {
    if (!isLogin) api.roadmaps('en').then(setCareers).catch(() => setCareers([]))
  }, [isLogin])

  if (user) return <Navigate to="/" replace />

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setUser(isLogin ? await api.login(email, password) : await api.register(email, password, name, path))
      await savePendingQuiz()
      navigate('/')
    } catch (problem) {
      setError((problem as ApiError).message)
      setBusy(false)
    }
  }

  return (
    <div className="card mx-auto mt-6 max-w-md">
      <h1 className="text-2xl">{isLogin ? 'Log in to My Path' : 'Create your free account'}</h1>
      <p className="mb-4 mt-1 text-sm text-muted">
        {isLogin
          ? 'You will go straight to your path: next steps, progress, what is changing and opportunities.'
          : 'Choose your career, and your path and progress will be saved to your account on any phone or computer.'}
      </p>
      <Notice kind="error">{error}</Notice>
      <form onSubmit={submit}>
        {!isLogin && (
          <Field label="Your name (optional)">
            <input className="input" value={name} maxLength={100} autoComplete="name" onChange={(event) => setName(event.target.value)} />
          </Field>
        )}
        {!isLogin && (
          <Field label="Choose your career path" hint="This becomes your path. It stays fixed for your account, so choose carefully.">
            <select className="input" required value={path} onChange={(event) => setPath(event.target.value)}>
              <option value="">Choose a career</option>
              {careers.map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
            </select>
          </Field>
        )}
        {!isLogin && !path && (
          <p className="-mt-2 mb-3 text-sm">Not sure yet? <Link to="/choose">Explore careers first</Link>, then come back.</p>
        )}
        <Field label="Email">
          <input className="input" type="email" required value={email} autoComplete="email" onChange={(event) => setEmail(event.target.value)} />
        </Field>
        <Field label="Password" hint={isLogin ? undefined : 'At least 10 characters. Not only numbers.'}>
          <input
            className="input" type="password" required value={password}
            minLength={isLogin ? undefined : 10}
            autoComplete={isLogin ? 'current-password' : 'new-password'}
            onChange={(event) => setPassword(event.target.value)}
          />
        </Field>
        <button type="submit" disabled={busy} className="btn btn-primary w-full">
          {busy ? 'Please wait…' : isLogin ? 'Log in' : 'Sign up'}
        </button>
      </form>
      <p className="mt-4 text-sm">
        {isLogin ? <>New here? <Link to="/register">Create an account</Link></> : <>Already have an account? <Link to="/login">Log in</Link></>}
      </p>
    </div>
  )
}

export const Login = () => <AuthPage mode="login" />
export const Register = () => <AuthPage mode="register" />
