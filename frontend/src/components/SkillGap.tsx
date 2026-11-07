import { useState } from 'react'
import type { Skill } from '../api/client'

const STORAGE_KEY = 'careerpath-my-skills'

function saved(): string[] {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

/** Compares what a student can do with what the chosen path needs. Saved only in this browser. */
export function SkillGap({ skills: all, career }: { skills: Skill[]; career: string }) {
  const [have, setHave] = useState<string[]>(saved)
  // Skills for this career come first, then skills every career needs
  const skills = [...all.filter((skill) => !skill.for_all), ...all.filter((skill) => skill.for_all)]
  const done = skills.filter((skill) => have.includes(skill.slug))
  const missing = skills.filter((skill) => !have.includes(skill.slug))
  const next = missing[0]

  function toggle(slug: string) {
    const updated = have.includes(slug) ? have.filter((item) => item !== slug) : [...have, slug]
    setHave(updated)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    } catch {
      // Private browsing can block storage. The ticks still work until the page closes.
    }
  }

  return (
    <section className="mt-8">
      <h2 className="text-2xl">Your skill gap</h2>
      <p className="mt-1">Tick what you can already do for {career}. You have {done.length} of {skills.length} skills.</p>
      <progress className="mt-2 w-full" value={done.length} max={skills.length} aria-label="Skills done" />
      {next
        ? <p className="mt-2 rounded-lg bg-pine-soft p-3"><strong>Learn next: {next.name}.</strong> {next.why}</p>
        : <p className="mt-2 rounded-lg bg-pine-soft p-3"><strong>You've ticked every skill here.</strong> Keep building projects to prove them.</p>}
      <ul className="mt-3 grid gap-2 md:grid-cols-2">
        {skills.map((skill) => (
          <li key={skill.slug}>
            <label className="flex items-start gap-2">
              <input type="checkbox" className="mt-1" checked={have.includes(skill.slug)} onChange={() => toggle(skill.slug)} />
              <span>{skill.name}</span>
            </label>
          </li>
        ))}
      </ul>
    </section>
  )
}
