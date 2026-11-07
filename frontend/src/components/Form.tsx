import type { ReactNode } from 'react'

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="mb-4 block">
      <span className="mb-1 block font-semibold">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-sm text-muted">{hint}</span>}
    </label>
  )
}

export function Notice({ kind, children }: { kind: 'error' | 'success'; children: ReactNode }) {
  if (!children) return null
  const colours = kind === 'error' ? 'border-[#f5b5ae] bg-[#fdecea]' : 'border-[#b9dfbf] bg-[#eaf6ec]'
  return <p role={kind === 'error' ? 'alert' : 'status'} className={`mb-4 rounded-lg border p-3 ${colours}`}>{children}</p>
}
