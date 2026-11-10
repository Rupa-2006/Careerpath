import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, type ApiError } from '../api/client'
import { Field, Notice } from '../components/Form'

/** Step 1: ask for a code by email. Step 2: type the code and a new password. */
export function ForgotPassword() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')
  const [sent, setSent] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function ask(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setSent((await api.forgotPassword(email)).message)
    } catch (problem) {
      setError((problem as ApiError).message)
    } finally {
      setBusy(false)
    }
  }

  async function reset(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api.resetPassword(email, code.trim(), password)
      navigate('/login?reset=1')
    } catch (problem) {
      setError((problem as ApiError).message)
      setBusy(false)
    }
  }

  return (
    <div className="card mx-auto mt-6 max-w-md">
      <h1 className="text-2xl">Forgot your password?</h1>
      <Notice kind="error">{error}</Notice>
      {!sent ? (
        <form onSubmit={ask} className="mt-3">
          <p className="mb-3 text-sm text-muted">Enter the email you signed up with. We'll send you a 6-digit code.</p>
          <Field label="Email">
            <input className="input" type="email" required value={email} autoComplete="email" onChange={(event) => setEmail(event.target.value)} />
          </Field>
          <button type="submit" disabled={busy} className="btn btn-primary w-full">{busy ? 'Please wait…' : 'Send me a code'}</button>
        </form>
      ) : (
        <form onSubmit={reset} className="mt-3">
          <p className="mb-3 rounded-lg bg-pine-soft p-3 text-sm">{sent} The code works once and expires in 30 minutes.</p>
          <Field label="6-digit code">
            <input
              className="input tracking-[0.3em]" required inputMode="numeric" autoComplete="one-time-code" maxLength={6} pattern="\d{6}"
              value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, ''))}
            />
          </Field>
          <Field label="New password" hint="At least 10 characters. Not only numbers.">
            <input className="input" type="password" required minLength={10} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </Field>
          <button type="submit" disabled={busy} className="btn btn-primary w-full">{busy ? 'Please wait…' : 'Change my password'}</button>
          <button type="button" className="mt-3 cursor-pointer text-sm text-teal underline" onClick={() => { setSent(''); setCode('') }}>Send a new code</button>
        </form>
      )}
      <p className="mt-4 text-sm"><Link to="/login">← Back to log in</Link></p>
    </div>
  )
}

export function ForgotUsername() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function ask(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      setSent((await api.forgotUsername(email)).message)
    } catch (problem) {
      setError((problem as ApiError).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="card mx-auto mt-6 max-w-md">
      <h1 className="text-2xl">Forgot your username?</h1>
      <Notice kind="error">{error}</Notice>
      {sent ? (
        <p className="mt-3 rounded-lg bg-pine-soft p-3 text-sm">{sent}</p>
      ) : (
        <form onSubmit={ask} className="mt-3">
          <p className="mb-3 text-sm text-muted">Enter the email you signed up with. We'll email you your username.</p>
          <Field label="Email">
            <input className="input" type="email" required value={email} autoComplete="email" onChange={(event) => setEmail(event.target.value)} />
          </Field>
          <button type="submit" disabled={busy} className="btn btn-primary w-full">{busy ? 'Please wait…' : 'Email me my username'}</button>
        </form>
      )}
      <p className="mt-4 text-sm"><Link to="/login">← Back to log in</Link></p>
    </div>
  )
}
