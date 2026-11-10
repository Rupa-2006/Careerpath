import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { api, type AdminSummary, type AdminUser, type ApiError } from '../api/client'
import { Notice } from '../components/Form'
import { ImportReview } from '../components/ImportReview'
import { PathRequestsAdmin } from '../components/PathChange'
import { ReportsAdmin } from '../components/ReportsAdmin'
import { ReviewQueue } from '../components/ReviewQueue'
import { WatchAlerts } from '../components/WatchAlerts'
import { useAuth } from '../context/AuthContext'

const STATS: [keyof AdminSummary, string][] = [
  ['students', 'Students'],
  ['admins', 'Admins'],
  ['regions', 'States and UTs'],
  ['streams', 'Streams'],
  ['sources', 'Sources'],
  ['pending_verification', 'Awaiting review'],
]

export function Admin() {
  const { user } = useAuth()
  const [summary, setSummary] = useState<AdminSummary | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(async (search: string) => {
    setError('')
    try {
      const [loadedSummary, list] = await Promise.all([api.adminSummary(), api.adminUsers(search)])
      setSummary(loadedSummary)
      setUsers(list.users)
      setTotal(list.total)
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }, [])

  useEffect(() => {
    load('')
  }, [load])

  function search(event: FormEvent) {
    event.preventDefault()
    load(query)
  }

  async function toggle(target: AdminUser) {
    try {
      await api.adminUpdateUser(target.id, { is_active: !target.is_active })
      await load(query)
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  return (
    <>
      <h1 className="text-3xl">Admin</h1>
      <Notice kind="error">{error}</Notice>
      <dl className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-6">
        {STATS.map(([key, label]) => (
          <div key={key} className="card">
            <dt className="text-sm text-muted">{label}</dt>
            <dd className="text-2xl font-bold text-pine">{summary?.[key] ?? '–'}</dd>
          </div>
        ))}
      </dl>

      <WatchAlerts />
      <PathRequestsAdmin />
      <ReportsAdmin />
      <ImportReview />
      <ReviewQueue onChange={() => load(query)} />

      <h2 className="mt-8 text-2xl">Users ({total})</h2>
      <form onSubmit={search} className="my-3 flex max-w-md gap-2">
        <input className="input" type="search" aria-label="Search users" placeholder="Search by name or email" maxLength={100} value={query} onChange={(event) => setQuery(event.target.value)} />
        <button type="submit" className="btn btn-primary">Search</button>
      </form>
      <div className="overflow-x-auto rounded-xl border border-line bg-white">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead className="bg-pine-soft">
            <tr><th className="p-3">Email</th><th className="p-3">Name</th><th className="p-3">Role</th><th className="p-3">Status</th><th className="p-3"><span className="sr-only">Actions</span></th></tr>
          </thead>
          <tbody>
            {users.map((item) => (
              <tr key={item.id} className="border-t border-line">
                <td className="p-3">{item.email}</td>
                <td className="p-3">{item.name ?? '–'}</td>
                <td className="p-3">{item.role}</td>
                <td className="p-3">{item.is_active ? 'Active' : 'Deactivated'}</td>
                <td className="p-3 text-right">
                  {item.id !== user?.id && (
                    <button type="button" className="btn btn-outline !min-h-9 !px-3 !py-1 text-sm" onClick={() => toggle(item)}>
                      {item.is_active ? 'Deactivate' : 'Reactivate'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {users.length === 0 && <tr><td colSpan={5} className="p-4 text-muted">No users found.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  )
}
