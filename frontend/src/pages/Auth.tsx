import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api, type ApiError } from '../api/client'
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
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const isLogin = mode === 'login'

  if (user) return <Navigate to="/my-path" replace />

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setUser(isLogin ? await api.login(email, password) : await api.register(email, password, name))
      await savePendingQuiz()
      navigate('/my-path')
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
          ? 'Your chosen career, finished steps, notes and skills will appear here.'
          : 'Save your path and progress, and see them on any phone or computer. Anything you already ticked on this device moves into your account.'}
      </p>
      <Notice kind="error">{error}</Notice>
      <form onSubmit={submit}>
        {!isLogin && (
          <Field label="Your name (optional)">
            <input className="input" value={name} maxLength={100} autoComplete="name" onChange={(event) => setName(event.target.value)} />
          </Field>
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
