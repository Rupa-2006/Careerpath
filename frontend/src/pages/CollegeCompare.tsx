import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type ApiError, type CollegeDetail } from '../api/client'
import { CollegeAttribution } from '../components/CollegeAttribution'
import { Notice } from '../components/Form'

const facts = (college: CollegeDetail, kind: string) =>
  college.facts.filter((fact) => fact.kind === kind).map((fact) => fact.value).join(' ') || 'Not available'

const ROWS: [string, (college: CollegeDetail) => string | number][] = [
  ['Location', (college) => [college.district, college.region.name].filter(Boolean).join(', ')],
  ['Year established', (college) => college.year_established ?? 'Not listed'],
  ['College type', (college) => college.college_type ?? 'Not listed'],
  ['Management', (college) => college.management ?? 'Not listed'],
  ['Affiliated university', (college) => college.university_name ?? 'Not listed'],
  ['Courses', (college) => college.offerings.map((item) => item.course_name).join(', ') || 'Not available'],
  ['Fees', (college) => facts(college, 'fees')],
  ['Placements', (college) => facts(college, 'placements')],
  ['Facilities', (college) => facts(college, 'facilities')],
]

export function CollegeCompare() {
  const [params] = useSearchParams()
  const [colleges, setColleges] = useState<CollegeDetail[]>([])
  const [error, setError] = useState('')
  const ids = useMemo(() => (params.get('ids') ?? '').split(',').filter(Boolean), [params])

  useEffect(() => {
    if (ids.length >= 2) api.compareColleges(ids).then(setColleges).catch((problem: ApiError) => setError(problem.message))
  }, [ids])

  if (ids.length < 2) {
    return (
      <div className="py-10 text-center">
        <h1 className="text-3xl">Compare colleges</h1>
        <p className="mt-2 text-muted">Tick 2 or 3 colleges on the Colleges page to compare them.</p>
        <Link to="/colleges" className="btn btn-primary mt-4">Go to colleges</Link>
      </div>
    )
  }

  return (
    <>
      <p><Link to="/colleges">← All colleges</Link></p>
      <h1 className="mt-2 text-3xl">Compare colleges</h1>
      <Notice kind="error">{error}</Notice>
      <div className="mt-4 overflow-x-auto rounded-xl border border-line bg-white">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="bg-pine-soft">
            <tr>
              <td className="p-3" />
              {colleges.map((college) => (
                <th key={college.id} scope="col" className="p-3"><Link to={`/colleges/${college.id}`}>{college.name}</Link></th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(([label, value]) => (
              <tr key={label} className="border-t border-line align-top">
                <th scope="row" className="w-40 p-3 text-pine">{label}</th>
                {colleges.map((college) => <td key={college.id} className="p-3">{value(college)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <CollegeAttribution />
    </>
  )
}
