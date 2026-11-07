import { Link } from 'react-router-dom'
import type { CourseSummary, Eligibility, Trust } from '../api/client'
import { useLang, type TextKey } from '../context/Language'

const STATUS: Record<string, [TextKey, string]> = {
  published: ['st_published', 'bg-[#e3f4e5] text-[#1f5c23]'],
  verified: ['st_verified', 'bg-[#e3f4e5] text-[#1f5c23]'],
  pending_verification: ['awaiting', 'bg-[#fff1d6] text-[#7a4d00]'],
  unverified: ['st_unverified', 'bg-[#fff1d6] text-[#7a4d00]'],
  outdated: ['st_outdated', 'bg-[#fdecea] text-[#8c1d18]'],
}

export function TrustBadge({ status }: { status: string }) {
  const { t } = useLang()
  if (status === 'published') return null   // students only ever see reviewed records, so a label adds nothing
  const [label, colours] = STATUS[status] ?? (['st_unverified', 'bg-line'] as [TextKey, string])
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ${colours}`}>{t(label)}</span>
}

export function SourceLine({ record }: { record: Trust }) {
  const { t } = useLang()
  return (
    <p className="text-sm text-muted">
      {record.source
        ? <>Information from <a href={record.source.url} target="_blank" rel="noopener noreferrer">{record.source.name} ↗</a></>
        : t('no_source')}
      {record.last_updated && <> · updated {new Date(`${record.last_updated}T00:00:00`).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</>}
    </p>
  )
}

const ELIGIBILITY: Record<Eligibility['status'], [string, string]> = {
  eligible: ['Fits your subjects', 'bg-[#e3f4e5] text-[#1f5c23]'],
  not_eligible: ["Doesn't fit your subjects", 'bg-[#fdecea] text-[#8c1d18]'],
  need_subjects: ['Add your subjects to check', 'bg-pine-soft text-pine'],
  check: ['Check the official site', 'bg-[#fff1d6] text-[#7a4d00]'],
  no_rule: ['No confirmed rule yet', 'bg-[#eceff3] text-[#47525f]'],
}

export function EligibilityBadge({ eligibility }: { eligibility: Eligibility }) {
  const [label, colours] = ELIGIBILITY[eligibility.status]
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ${colours}`}>{label}</span>
}

export function EligibilityNote({ eligibility }: { eligibility: Eligibility }) {
  return (
    <div className="rounded-lg border border-line bg-paper p-3">
      <EligibilityBadge eligibility={eligibility} />
      <p className="mt-1 text-sm">{eligibility.message}</p>
      {eligibility.missing.length > 0 && <p className="mt-1 text-sm">You would need: {eligibility.missing.join('; ')}.</p>}
    </div>
  )
}

export function CourseCard({ course, onToggle, selected }: { course: CourseSummary; onToggle?: () => void; selected?: boolean }) {
  return (
    <li className="card flex flex-col gap-2">
      <div className="flex flex-wrap gap-1">
        <EligibilityBadge eligibility={course.eligibility} />
        <TrustBadge status={course.status} />
      </div>
      <h3 className="text-lg"><Link to={`/courses/${course.slug}`} className="text-pine">{course.name}</Link></h3>
      <p className="text-sm text-muted">{course.field_name} · {course.kind}</p>
      <p className="flex-1">{course.summary}</p>
      <p className="text-sm text-muted">{course.duration}</p>
      {course.eligibility.missing.length > 0 && <p className="text-sm">Needs: {course.eligibility.missing.join('; ')}</p>}
      {onToggle && (
        <label className="flex min-h-9 items-center gap-2 text-sm font-semibold text-teal">
          <input type="checkbox" checked={selected} onChange={onToggle} /> Compare
        </label>
      )}
    </li>
  )
}
