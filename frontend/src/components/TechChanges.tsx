import { useEffect, useState } from 'react'
import { api, type TechChange } from '../api/client'
import { SourceLine, TrustBadge } from './Trust'

const LEVELS: Record<string, string> = {
  essential: 'Essential: needed for this career',
  emerging: 'Emerging: growing in importance',
  optional: 'Optional: useful to know',
  outdated: 'Outdated: losing importance',
}

/** Verified changes in technology. Pass a roadmap to show only what affects that career. */
export function TechChanges({ roadmap = '', title }: { roadmap?: string; title: string }) {
  const [items, setItems] = useState<TechChange[]>([])

  useEffect(() => {
    api.techChanges(roadmap).then(setItems).catch(() => setItems([]))
  }, [roadmap])

  if (items.length === 0) return null
  return (
    <section className="mt-8">
      <h2 className="text-2xl">{title}</h2>
      <ul className="mt-3 grid gap-3 md:grid-cols-2">
        {items.map((item) => (
          <li key={item.slug} className="card">
            <h3 className="text-lg">{item.title}</h3>
            <p className="mt-1 text-sm font-semibold">{LEVELS[item.level] ?? item.level}</p>
            <div className="mt-1"><TrustBadge status={item.status} /></div>
            <p className="mt-2"><strong>What changed:</strong> {item.what_changed}</p>
            <p className="mt-1"><strong>Why it matters:</strong> {item.why_it_matters}</p>
            <p className="mt-1"><strong>Learn next:</strong> {item.learn_next}</p>
            <div className="mt-2"><SourceLine record={item} /></div>
          </li>
        ))}
      </ul>
    </section>
  )
}
