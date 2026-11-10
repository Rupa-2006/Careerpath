import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useMyPath } from '../context/useMyCourse'
import { AreaGrid } from './Choose'

const JOURNEY = [
  ['Choose an area', 'Pick an area, then a course and a career.'],
  ['Follow the path', 'See what to learn and do, step by step.'],
  ['Keep up with change', 'See what is changing in your field, and what to learn because of it.'],
  ['Reach your opportunity', 'See the jobs, study and other options at the end of your path.'],
]

/** The two ways to use the site: look around freely, or follow and save your own path. */
function TwoWays() {
  const { user } = useAuth()
  const { slug } = useMyPath()
  const name = user?.name?.split(' ')[0]
  return (
    <section className="mt-6 grid gap-4 md:grid-cols-2" aria-label="Two ways to use CareerPath">
      <div className="card flex flex-col border-t-4 border-t-teal">
        <p className="text-3xl" aria-hidden="true">🧭</p>
        <h2 className="mt-2 text-2xl">Explore careers</h2>
        <p className="mt-1 text-muted">Look at every area, course, career and roadmap. No login needed.</p>
        <div className="mt-auto pt-4">
          <a href="#careers" className="btn btn-primary">Start exploring ↓</a>
        </div>
      </div>
      <div className="card flex flex-col border-t-4 border-t-sun">
        <p className="text-3xl" aria-hidden="true">🎯</p>
        <h2 className="mt-2 text-2xl">My Path</h2>
        {user ? (
          <>
            <p className="mt-1 text-muted">
              {name ? `Welcome back, ${name}. ` : 'Welcome back. '}
              {slug ? 'Your progress is saved to your account, on every device.' : 'Choose your career, and your progress will be saved to your account.'}
            </p>
            <div className="mt-auto pt-4">
              <Link to="/my-path" className="btn btn-primary">{slug ? 'Continue my path →' : 'Choose my career →'}</Link>
            </div>
          </>
        ) : (
          <>
            <p className="mt-1 text-muted">Follow your chosen career step by step. Log in to save your progress and see it on any phone or computer.</p>
            <div className="mt-auto flex flex-wrap items-center gap-2 pt-4">
              <Link to="/login" className="btn btn-primary">Log in</Link>
              <Link to="/register" className="btn btn-outline">Sign up free</Link>
              <Link to="/my-path" className="text-sm">or continue without login</Link>
            </div>
          </>
        )}
      </div>
    </section>
  )
}

export function Home() {
  return (
    <>
      <section className="relative overflow-hidden rounded-2xl bg-pine px-6 py-10 text-white md:px-12 md:py-14">
        <div className="relative max-w-2xl">
          <h1 className="text-4xl text-white md:text-5xl">What do you want to become?</h1>
          <p className="mt-4 text-lg text-white/90">You've finished Intermediate. Choose a direction, and we'll show you the path, what's changing, and where it can take you.</p>
          <p className="mt-2 font-semibold text-white">For students in Andhra Pradesh and Telangana.</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href="#careers" className="btn btn-sun">Start here ↓</a>
            <Link to="/quiz" className="btn border-2 border-white/60 text-white hover:bg-white/10">Not sure? Take the quiz</Link>
          </div>
        </div>
      </section>

      <TwoWays />

      <ol className="mt-6 flex flex-wrap items-center gap-2 text-sm font-semibold text-pine" aria-label="How it works">
        {JOURNEY.map(([title], index) => (
          <li key={title} className="flex items-center gap-2">
            {index > 0 && <span aria-hidden="true" className="text-muted">→</span>}
            <span className="rounded-full bg-pine-soft px-3 py-1">{index + 1}. {title}</span>
          </li>
        ))}
      </ol>

      <section id="careers" className="mt-8 scroll-mt-20">
        <h2 className="text-2xl">What area interests you?</h2>
        <p className="mb-4 mt-1 text-muted">Pick one to see its courses and branches.</p>
        <AreaGrid />
        <p className="mt-5"><Link to="/roadmaps" className="font-semibold">Already know your career? Search all 30 →</Link></p>
      </section>
    </>
  )
}
