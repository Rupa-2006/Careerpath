import type { useBackground } from '../context/useBackground'
import { Field, Notice } from './Form'

// CareerPath is built first for these two states, so they come first in the list
const FOCUS_STATES = ['AP', 'TS']

export function BackgroundForm({ state }: { state: ReturnType<typeof useBackground> }) {
  const { background, choose, regions, streams, subjects, error, savedToAccount, loggedIn } = state
  const stream = streams.find((item) => item.id === background.stream_id)
  const isFocus = (code: string) => FOCUS_STATES.includes(code)
  const places = (kind: string) => regions.filter((region) => region.kind === kind && !isFocus(region.code))

  function toggleSubject(id: number) {
    const has = background.subject_ids.includes(id)
    choose({ subject_ids: has ? background.subject_ids.filter((item) => item !== id) : [...background.subject_ids, id] })
  }

  return (
    <section className="card">
      <Notice kind="error">{error}</Notice>
      <div className="grid gap-x-4 sm:grid-cols-2">
        <Field label="Your State or Union Territory">
          <select className="input" value={background.region_id ?? ''} onChange={(event) => choose({ region_id: Number(event.target.value) || null })}>
            <option value="">Choose one</option>
            {regions.filter((item) => isFocus(item.code)).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            <optgroup label="Other States">{places('state').map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</optgroup>
            <optgroup label="Union Territories">{places('union_territory').map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</optgroup>
          </select>
        </Field>
        <Field label="What you studied in Class 12">
          <select className="input" value={background.stream_id ?? ''} onChange={(event) => choose({ stream_id: Number(event.target.value) || null })}>
            <option value="">Choose one</option>
            {streams.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}{item.aliases.length > 0 ? ` (${item.aliases.join(', ')})` : ''}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {stream && stream.subjects.length > 0 && (
        <p className="text-sm text-muted">Usual subjects: {stream.subjects.map((subject) => subject.name).join(', ')}</p>
      )}
      <details className="mt-2" open={background.subject_ids.length > 0}>
        <summary className="min-h-11 cursor-pointer py-2 font-semibold text-teal">My subjects are different</summary>
        <p className="text-sm text-muted">Tick your exact subjects. These replace the usual subjects above.</p>
        <div className="mt-2 grid gap-1 sm:grid-cols-2 lg:grid-cols-3">
          {subjects.map((subject) => (
            <label key={subject.id} className="flex min-h-9 items-center gap-2">
              <input type="checkbox" checked={background.subject_ids.includes(subject.id)} onChange={() => toggleSubject(subject.id)} />
              {subject.name}
            </label>
          ))}
        </div>
      </details>
      <p className="mt-2 text-sm text-muted">
        {loggedIn ? (savedToAccount ? 'Saved to your account.' : 'Your State and stream are saved to your account.') : 'Saved on this device only. Sign up to keep it in your account.'}
      </p>
    </section>
  )
}
