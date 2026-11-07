import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ApiError, type RoadmapSummary, type Skill } from '../api/client'
import { Notice } from '../components/Form'
import { ReportForm } from '../components/Journey'
import { SourceLine, TrustBadge } from '../components/Trust'
import { useAuth } from '../context/AuthContext'
import { useLang, type TextKey } from '../context/Language'

const CATEGORIES = ['communication', 'thinking', 'aptitude', 'programming', 'technical', 'domain', 'certifications', 'internship'] as const
const categoryKey = (category: string) => `cat_${category}` as TextKey

function SkillCard({ skill, canTrack, onChange }: { skill: Skill; canTrack: boolean; onChange: (state: Skill['state']) => void }) {
  const { t } = useLang()
  const choice = (state: 'learning' | 'done', label: TextKey) => (
    <button
      type="button" aria-pressed={skill.state === state} onClick={() => onChange(state)}
      className={`btn !min-h-9 !px-3 !py-1 text-sm ${skill.state === state ? 'btn-primary' : 'btn-outline'}`}
    >
      {skill.state === state ? '✓ ' : ''}{t(label)}
    </button>
  )

  return (
    <li className={`card flex flex-col gap-2 ${skill.state === 'done' ? 'border-[#2e7d32] bg-[#f4fbf5]' : ''}`}>
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="flex-1 basis-40 text-lg">{skill.name}</h3>
        <TrustBadge status={skill.status} />
      </div>
      <p>{skill.why}</p>
      <p className="rounded-lg bg-[#fff7e6] p-2"><strong>🛠 {t('try_project')}:</strong> {skill.project}</p>
      <p className="flex flex-wrap items-center gap-2">
        <strong>{t('where_learn')}:</strong>
        {skill.resources.map((link) => (
          <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer" className="rounded-full border border-line px-3 py-0.5 text-sm no-underline hover:border-teal">{link.label} ↗</a>
        ))}
      </p>
      {canTrack && (
        <div className="mt-auto flex flex-wrap gap-2 pt-1">
          {choice('learning', 'state_learning')}
          {choice('done', 'state_done')}
          {skill.state && <button type="button" className="cursor-pointer text-sm text-muted underline" onClick={() => onChange(null)}>{t('state_clear')}</button>}
        </div>
      )}
      <SourceLine record={skill} />
    </li>
  )
}

export function Skills() {
  const { t, lang } = useLang()
  const { user } = useAuth()
  const [skills, setSkills] = useState<Skill[] | null>(null)
  const [roadmaps, setRoadmaps] = useState<RoadmapSummary[]>([])
  const [roadmap, setRoadmap] = useState('')
  const [category, setCategory] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(() => {
    api.skills(lang, roadmap).then(setSkills).catch((problem: ApiError) => setError(problem.message))
  }, [lang, roadmap])

  useEffect(load, [load, user])

  useEffect(() => {
    api.roadmaps(lang).then(setRoadmaps).catch(() => setRoadmaps([]))
  }, [lang])

  async function change(skill: Skill, state: Skill['state']) {
    setError('')
    try {
      await (state && state !== skill.state ? api.setSkill(skill.id, state) : api.clearSkill(skill.id))
      load()
    } catch (problem) {
      setError((problem as ApiError).message)
    }
  }

  const shown = (skills ?? []).filter((skill) => !category || skill.category === category)
  const groups = CATEGORIES.filter((item) => shown.some((skill) => skill.category === item))
  const done = (skills ?? []).filter((skill) => skill.state === 'done').length
  const learning = (skills ?? []).filter((skill) => skill.state === 'learning').length
  const total = skills?.length ?? 0

  return (
    <>
      <h1 className="text-3xl">{t('skills_title')}</h1>
      <p className="mt-2 max-w-2xl text-muted">{t('skills_help')}</p>
      <Notice kind="error">{error}</Notice>

      {total > 0 && (
        <section className="card mt-4 max-w-3xl">
          {user ? (
            <>
              <h2 className="text-xl">{t('my_checklist')}</h2>
              <p className="mb-1 mt-1">{done} / {total} {t('skills_done')} · {learning} {t('learning_now')}</p>
              <progress max={total} value={done} className="h-3 w-full accent-teal" />
            </>
          ) : (
            <p>{t('log_in_skills')} <Link to="/login">{t('log_in')}</Link> · <Link to="/register">{t('sign_up')}</Link></p>
          )}
        </section>
      )}

      <div className="mt-4 max-w-sm">
        <label>
          <span className="mb-1 block font-semibold">{t('skills_for')}</span>
          <select className="input" value={roadmap} onChange={(event) => setRoadmap(event.target.value)}>
            <option value="">{t('all_careers')}</option>
            {roadmaps.map((item) => <option key={item.slug} value={item.slug}>{item.name}</option>)}
          </select>
        </label>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
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
              <SkillCard key={skill.id} skill={skill} canTrack={Boolean(user)} onChange={(state) => change(skill, state)} />
            ))}
          </ul>
        </section>
      ))}
      <ReportForm />
    </>
  )
}
