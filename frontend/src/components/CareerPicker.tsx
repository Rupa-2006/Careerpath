import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type RoadmapSummary } from '../api/client'

const GROUPS: [string, string[]][] = [
  ['Technology', ['web-developer', 'ai-engineer', 'cyber-security-analyst', 'data-analyst']],
  ['Engineering', ['embedded-engineer', 'electrical-engineer', 'mechanical-engineer', 'civil-engineer', 'architect']],
  ['Health', ['doctor', 'nurse', 'dentist', 'pharmacist', 'physiotherapist', 'health-technologist', 'traditional-medicine-doctor']],
  ['Business and finance', ['accounts-finance', 'business-manager', 'company-secretary', 'hotel-manager']],
  ['Law and public service', ['advocate', 'civil-services', 'government-exams', 'defence-officer', 'social-worker']],
  ['Science, land and animals', ['researcher', 'agriculture-officer', 'animal-and-fisheries']],
  ['Creative and hands-on', ['designer', 'pilot', 'physical-education-teacher', 'vocational-professional']],
]

const POPULAR = ['web-developer', 'cyber-security-analyst', 'data-analyst', 'doctor', 'accounts-finance', 'civil-services']

/** The front door of the site: pick where you want to go. */
export function CareerPicker({ popular = false }: { popular?: boolean }) {
  const [items, setItems] = useState<RoadmapSummary[]>([])
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.roadmaps('en').then(setItems).catch(() => setItems([]))
  }, [])

  const words = query.trim().toLowerCase()
  const groups = useMemo(() => GROUPS.map(([name, slugs]) => [
    name,
    slugs.map((slug) => items.find((item) => item.slug === slug)).filter((item): item is RoadmapSummary => (
      Boolean(item) && (!words || `${item?.name} ${item?.description}`.toLowerCase().includes(words))
    )),
  ] as const).filter(([, found]) => found.length > 0), [items, words])

  return (
    <>
      <label className="block max-w-xl font-semibold">
        Search for a career
        <input className="input mt-1 w-full font-normal" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="For example, cyber security or doctor" />
      </label>
      {popular && !words && (
        <>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {POPULAR.map((slug) => items.find((item) => item.slug === slug)).filter((item) => item !== undefined).map((item) => (
              <li key={item.slug}>
                <Link to={`/roadmaps/${item.slug}`} className="card block h-full text-ink no-underline hover:border-teal">
                  <span className="font-bold text-pine">{item.name}</span>
                  <span className="mt-1 block text-sm text-muted">{item.description}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/roadmaps" className="btn btn-outline mt-4">See all {items.length} careers</Link>
        </>
      )}
      {items.length > 0 && groups.length === 0 && <p className="mt-4 text-muted">No career matches that yet. Try another word.</p>}
      {(!popular || words) && groups.map(([name, found]) => (
        <section key={name} className="mt-6">
          <h3 className="text-lg">{name}</h3>
          <ul className="mt-2 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {found.map((item) => (
              <li key={item.slug}>
                <Link to={`/roadmaps/${item.slug}`} className="card block h-full text-ink no-underline hover:border-teal">
                  <span className="font-bold text-pine">{item.name}</span>
                  <span className="mt-1 block text-sm text-muted">{item.description}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}
