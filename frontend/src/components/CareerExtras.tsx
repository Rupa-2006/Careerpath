import { useEffect, useState } from 'react'
import { api, type CareerGrowth, type CareerOpportunity, type TechChange, type UpdateItem } from '../api/client'
import { TrustBadge } from './Trust'

/** How someone commonly grows in this career, and what to have ready for a first job. */
export function CareerLadder({ roadmap }: { roadmap: string }) {
  const [growth, setGrowth] = useState<CareerGrowth | null>(null)

  useEffect(() => {
    api.careerGrowth(roadmap).then(setGrowth).catch(() => setGrowth(null))
  }, [roadmap])

  if (!growth) return null
  const ladder = [['First role', growth.first], ['With experience', growth.next], ['Senior role', growth.senior]]
  return (
    <section className="mt-6">
      <h2 className="text-2xl">How you can grow</h2>
      <ol className="mt-3 grid gap-3 md:grid-cols-3">
        {ladder.map(([label, role], index) => (
          <li key={label} className="card border-t-4 border-t-teal">
            <span className="text-sm font-semibold text-teal">{index + 1}. {label}</span>
            <p className="mt-1 font-bold text-pine">{role}</p>
          </li>
        ))}
      </ol>
      <p className="mt-2 text-sm text-muted">This is a common pattern. Job titles and timing differ between employers.</p>
      <h2 className="mt-6 text-2xl">Ready for your first job?</h2>
      <ul className="mt-2 grid gap-1">
        {growth.ready.map((item) => <li key={item} className="flex gap-2"><span aria-hidden="true" className="text-teal">✓</span>{item}</li>)}
      </ul>
    </section>
  )
}

const FOR_BTECH = 'M.Tech or MS after a B.Tech, or MCA or M.Sc after BCA or B.Sc. Many M.Tech seats in India use the GATE exam.'

/** Some careers are shared by related courses, so the study advice follows the course the student chose. */
function forCourse(detail: string, course: string) {
  if (course.startsWith('btech')) return detail.replace(FOR_BTECH, 'M.Tech or MS. Many M.Tech seats in India use the GATE exam.')
  if (course === 'bca' || course === 'bsc-cs') return detail.replace(FOR_BTECH, 'MCA or M.Sc.')
  return detail
}

/** What opens up once a student finishes this roadmap. */
export function AfterRoadmap({ roadmap, course = '', title = "Where this path can take you" }: { roadmap: string; course?: string; title?: string }) {
  const [items, setItems] = useState<CareerOpportunity[]>([])

  useEffect(() => {
    api.careerOpportunities(roadmap).then(setItems).catch(() => setItems([]))
  }, [roadmap])

  if (items.length === 0) return null
  return (
    <section className="mt-8">
      <h2 className="text-2xl">{title}</h2>
      <p className="mt-1 text-sm text-muted">These are common next steps, not job guarantees. The links go to places that list real openings.</p>
      <ul className="mt-3 grid gap-3 md:grid-cols-2">
        {items.map((item) => (
          <li key={item.kind} className="card">
            <h3 className="text-lg">{item.title}</h3>
            <p className="mt-1">{forCourse(item.detail, course)}</p>
            <div className="mt-2 flex flex-wrap items-center gap-3">
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold">{new URL(item.url).hostname.replace(/^www\./, '')} ↗</a>
              <TrustBadge status={item.status} />
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

/** Headlines collected automatically from sources matched to this career. */
export function CareerNews({ roadmap }: { roadmap: string }) {
  const [items, setItems] = useState<UpdateItem[]>([])

  useEffect(() => {
    api.careerUpdates(roadmap).then(setItems).catch(() => setItems([]))
  }, [roadmap])

  if (items.length === 0) return null
  return (
    <section className="mt-8">
      <h2 className="text-2xl">Latest in this field</h2>
      <p className="mt-1 text-sm text-muted">Collected automatically from these sources. This is news, not advice, and it isn't reviewed by us.</p>
      <ul className="mt-3 grid gap-2">
        {items.slice(0, 3).map((item) => (
          <li key={item.link} className="card">
            <a href={item.link} target="_blank" rel="noopener noreferrer" className="font-semibold">{item.title} ↗</a>
            <p className="text-sm text-muted">{item.source_name}{item.published_at ? ` · ${new Date(item.published_at).toLocaleDateString('en-IN')}` : ''}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}

/** Says so plainly when nothing has been found for a career yet, instead of showing a blank tab. */
export function EmptyChanges({ roadmap }: { roadmap: string }) {
  const [state, setState] = useState<{ changes: TechChange[]; news: UpdateItem[] } | null>(null)

  useEffect(() => {
    Promise.all([api.techChanges(roadmap), api.careerUpdates(roadmap)])
      .then(([changes, news]) => setState({ changes, news }))
      .catch(() => setState(null))
  }, [roadmap])

  if (!state || state.changes.length > 0 || state.news.length > 0) return null
  return <p className="mt-6 text-muted">We don't have confirmed updates for this career yet.</p>
}
