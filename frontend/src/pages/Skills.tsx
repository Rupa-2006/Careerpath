import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type RoadmapSummary, type Skill } from '../api/client'
import { Notice } from '../components/Form'
import { ReportForm } from '../components/Journey'
import { SourceLine } from '../components/Trust'
import { useMyPath, useMySkills } from '../context/useMyCourse'
import { useLang, type TextKey } from '../context/Language'

const CATEGORIES = ['communication', 'thinking', 'aptitude', 'programming', 'technical', 'domain', 'certifications', 'internship'] as const
const categoryKey = (category: string) => `cat_${category}` as TextKey
function SkillCard({ skill, have, onToggle }: { skill: Skill; have: boolean; onToggle: () => void }) {
  const { t } = useLang()
  return (
    <li className={`card flex flex-col gap-2 ${have ? 'border-[#2e7d32] bg-[#f4fbf5]' : ''}`}>
      <h3 className="text-lg">{skill.name}</h3>
      <p>{skill.why}</p>
      <p className="rounded-lg bg-[#fff7e6] p-2"><strong>🛠 {t('try_project')}:</strong> {skill.project}</p>
      <p className="flex flex-wrap items-center gap-2">
        <strong>{t('where_learn')}:</strong>
        {skill.resources.map((link) => (
          <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer" className="rounded-full border border-line px-3 py-0.5 text-sm no-underline hover:border-teal">{link.label} ↗</a>
        ))}
      </p>
      <div className="mt-auto pt-1">
        <button
          type="button" aria-pressed={have} onClick={onToggle}
          className={`btn !min-h-9 !px-3 !py-1 text-sm ${have ? 'btn-primary' : 'btn-outline'}`}
        >
          {have ? '✓ I can do this' : 'I can do this'}
        </button>
      </div>
      <SourceLine record={skill} />
    </li>
  )
}

export function Skills() {
  const { t, lang } = useLang()
  const { slug: myPath } = useMyPath()
  const [skills, setSkills] = useState<Skill[] | null>(null)
  const [roadmaps, setRoadmaps] = useState<RoadmapSummary[]>([])
  const [roadmap, setRoadmap] = useState(myPath)
  const [category, setCategory] = useState('')
  const { have, toggle } = useMySkills()
  const [error, setError] = useState('')

  useEffect(() => {
    api.skills(lang, roadmap).then(setSkills).catch((problem: ApiError) => setError(problem.message))
  }, [lang, roadmap])

  useEffect(() => {
    api.roadmaps(lang).then(setRoadmaps).catch(() => setRoadmaps([]))
  }, [lang])

  const all = skills ?? []
  const shown = all.filter((skill) => !category || skill.category === category)
  const groups = CATEGORIES.filter((item) => shown.some((skill) => skill.category === item))
  const done = all.filter((skill) => have.includes(skill.slug)).length
  const career = roadmaps.find((item) => item.slug === roadmap)?.name

  return (
    <>
      <h1 className="text-3xl">{t('skills_title')}</h1>
      <p className="mt-2 max-w-2xl text-muted">{t('skills_help')}</p>
      <Notice kind="error">{error}</Notice>

      <section className="card mt-4 max-w-3xl">
        <label>
          <span className="mb-1 block font-semibold">{t('skills_for')}</span>
          <select className="input max-w-sm" value={roadmap} onChange={(event) => setRoadmap(event.target.value)}>
            <option value="">{t('all_careers')}</option>
            {roadmaps.map((item) => <option key={item.slug} value={item.slug}>{item.name}{item.slug === myPath ? ' (my path)' : ''}</option>)}
          </select>
        </label>
        {all.length > 0 && (
          <>
            <p className="mb-1 mt-3">
              You can do <strong>{done} of {all.length}</strong> skills{career ? ` for ${career}` : ''}. Your ticks stay on this device. No account is needed.
            </p>
            <progress max={all.length} value={done} className="h-3 w-full accent-teal" aria-label="Skills you can do" />
          </>
        )}
        {roadmap && <p className="mt-2 text-sm"><Link to={`/roadmaps/${roadmap}`}>See the full roadmap →</Link></p>}
      </section>

      <div className="mt-4 flex flex-wrap gap-2">
        {[['', t('all_skills')] as const, ...CATEGORIES.map((item) => [item, t(categoryKey(item))] as const)].map(([value, label]) => (
          <button
            key={value} type="button" aria-pressed={category === value} onClick={() => setCategory(value)}
            className={`btn !min-h-9 !px-3 !py-1 text-sm ${category === value ? 'btn-primary' : 'btn-outline'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {skills?.length === 0 && <p className="mt-4 text-muted">{t('skills_empty')}</p>}
      {groups.map((group) => (
        <section key={group}>
          <h2 className="mt-6 text-2xl">{t(categoryKey(group))}</h2>
          <ul className="mt-3 grid gap-4 md:grid-cols-2">
            {shown.filter((skill) => skill.category === group).map((skill) => (
              <SkillCard key={skill.id} skill={skill} have={have.includes(skill.slug)} onToggle={() => toggle(skill.slug)} />
            ))}
          </ul>
        </section>
      ))}
      <ReportForm />
    </>
  )
}
