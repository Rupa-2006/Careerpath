import { useEffect, useState } from 'react'
import { api, type ApiError, type ReportItem } from '../api/client'
import { Notice } from './Form'

export function ReportsAdmin() {
  const [reports, setReports] = useState<ReportItem[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.adminReports().then(setReports).catch((problem: ApiError) => setError(problem.message))
  }, [])

  async function resolve(id: number) {
    try {
      await api.resolveReport(id)
      setReports(await api.adminReports())
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  const open = reports.filter((report) => !report.resolved)

  return (
    <section className="mt-8">
      <h2 className="text-2xl">Mistake reports ({open.length})</h2>
      <Notice kind="error">{error}</Notice>
      {open.length === 0 && <p className="mt-1 text-muted">No open reports.</p>}
      <ul className="mt-3 grid gap-3">
        {open.map((report) => (
          <li key={report.id} className="card">
            <p className="text-sm text-muted">{report.page} · {report.created_at.slice(0, 10)}</p>
            <p className="mt-1">{report.message}</p>
            <button type="button" className="btn btn-outline mt-2 !min-h-9 !px-3 !py-1 text-sm" onClick={() => resolve(report.id)}>Mark as resolved</button>
          </li>
        ))}
      </ul>
    </section>
  )
}
