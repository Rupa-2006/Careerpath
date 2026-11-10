import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type ApiError } from '../api/client'
import { Field, Notice } from '../components/Form'
import { PathChange } from '../components/PathChange'
import { useAuth } from '../context/AuthContext'

export function Account() {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState(user?.name ?? '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [deletePassword, setDeletePassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function run(action: () => Promise<void>, success: string) {
    setError('')
    setMessage('')
    try {
      await action()
      setMessage(success)
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  function saveName(event: FormEvent) {
    event.preventDefault()
    run(async () => setUser(await api.updateProfile({ name })), 'Your name is saved.')
  }

  function savePassword(event: FormEvent) {
    event.preventDefault()
    run(async () => {
      await api.changePassword(currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
    }, 'Your password is changed. Your other devices have been logged out.')
  }

  async function removeAccount(event: FormEvent) {
    event.preventDefault()
    setError('')
    try {
      await api.deleteAccount(deletePassword)
      setUser(null)
      navigate('/')
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-3xl">My account</h1>
      <p className="mb-4 mt-1 text-muted">{user?.email}</p>
      <Notice kind="success">{message}</Notice>
      <Notice kind="error">{error}</Notice>

      <PathChange />

      <form onSubmit={saveName} className="card mb-4">
        <h2 className="mb-3 text-xl">Your name</h2>
        <Field label="Name">
          <input className="input" value={name} maxLength={100} autoComplete="name" onChange={(event) => setName(event.target.value)} />
        </Field>
        <button type="submit" className="btn btn-primary">Save name</button>
      </form>

      <form onSubmit={savePassword} className="card mb-4">
        <h2 className="mb-3 text-xl">Change password</h2>
        <Field label="Current password">
          <input className="input" type="password" required autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} />
        </Field>
        <Field label="New password" hint="At least 10 characters. Not only numbers.">
          <input className="input" type="password" required minLength={10} autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} />
        </Field>
        <button type="submit" className="btn btn-primary">Change password</button>
      </form>

      <form onSubmit={removeAccount} className="card">
        <h2 className="mb-1 text-xl">Delete my account</h2>
        <p className="mb-3 text-muted">This permanently removes your account and cannot be undone.</p>
        <Field label="Enter your password to confirm">
          <input className="input" type="password" required autoComplete="current-password" value={deletePassword} onChange={(event) => setDeletePassword(event.target.value)} />
        </Field>
        <button type="submit" className="btn btn-danger">Delete my account</button>
      </form>
    </div>
  )
}
