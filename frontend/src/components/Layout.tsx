import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useLang, type TextKey } from '../context/Language'

const NAV: [string, TextKey][] = [
  ['/', 'nav_home'],
  ['/choose', 'nav_roadmaps'],
  ['/my-path', 'nav_my_course'],
  ['/updates', 'nav_updates'],
  ['/all-courses', 'nav_courses'],
  ['/scholarships', 'nav_scholarships'],
  ['/assistant', 'nav_assistant'],
]

const navClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-2 py-2 text-sm text-white no-underline hover:bg-white/10 ${isActive ? 'bg-white/15 font-semibold' : ''}`

export function Layout() {
  const { user, logout } = useAuth()
  const { t } = useLang()
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    setOpen(false)
    window.scrollTo(0, 0)
  }, [location.pathname])

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main" className="absolute -left-96 top-2 rounded bg-white px-3 py-2 focus:left-2">{t('skip')}</a>
      <header className="sticky top-0 z-20 bg-pine text-white print:hidden">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 px-4 py-2">
          <Link to="/" className="text-xl font-extrabold text-white no-underline">
            Career<span className="text-sun">Path</span>
          </Link>

          <div className="ml-auto flex items-center gap-2 xl:order-3">
            {user ? (
              <>
                {user.role === 'admin' && <NavLink to="/admin" className={navClass}>Admin</NavLink>}
                <NavLink to="/my-progress" className={navClass}>{t('my_progress')}</NavLink>
                <NavLink to="/account" className={navClass}>{t('my_account')}</NavLink>
                <button type="button" onClick={handleLogout} className="cursor-pointer rounded-md px-2 py-2 text-sm hover:bg-white/10">{t('log_out')}</button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={navClass}>{t('log_in')}</NavLink>
                <Link to="/register" className="btn btn-sun !min-h-9 !px-3 !py-1 text-sm">{t('sign_up')}</Link>
              </>
            )}
            <button
              type="button"
              className="min-h-11 min-w-11 cursor-pointer rounded-md text-2xl hover:bg-white/10 xl:hidden"
              aria-label="Menu"
              aria-expanded={open}
              onClick={() => setOpen(!open)}
            >
              ☰
            </button>
          </div>

          <nav aria-label="Main" className={`${open ? 'flex' : 'hidden'} w-full flex-col pb-2 xl:order-2 xl:flex xl:w-auto xl:flex-row xl:pb-0`}>
            {NAV.map(([to, label]) => (
              <NavLink key={to} to={to} end={to === '/'} className={navClass}>{t(label)}</NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
        <Outlet />
      </main>

      <footer className="bg-pine px-4 py-6 text-sm text-white/85 print:hidden">
        <div className="mx-auto max-w-7xl">
          <p className="font-bold text-white">CareerPath: Discover Your Future</p>
          <p className="mt-1">{t('footer_note')}</p>
          <p className="mt-2 flex flex-wrap gap-4">
            <Link to="/quiz" className="text-white">{t('take_quiz')}</Link>
            <Link to="/skills" className="text-white">Skills checklist</Link>
            <Link to="/compare" className="text-white">Compare courses</Link>
            <Link to="/compare-careers" className="text-white">Compare careers</Link>
          </p>
        </div>
      </footer>
    </div>
  )
}
