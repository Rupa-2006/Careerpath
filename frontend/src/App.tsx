import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation, useParams } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AuthProvider, useAuth } from './context/AuthContext'
import { Account } from './pages/Account'
import { Admin } from './pages/Admin'
import { Assistant } from './pages/Assistant'
import { Login, Register } from './pages/Auth'
import { CollegeCompare } from './pages/CollegeCompare'
import { CollegeDetailPage } from './pages/CollegeDetail'
import { Colleges } from './pages/Colleges'
import { Compare } from './pages/Compare'
import { CompareCareers } from './pages/CompareCareers'
import { CourseDetailPage } from './pages/CourseDetail'
import { Home } from './pages/Home'
import { DatesPage, UpdatesPage } from './pages/Info'
import { AllCourses } from './pages/AllCourses'
import { ChooseArea, ChooseCareer, ChooseCourse } from './pages/Choose'
import { MyPath } from './pages/MyCourse'
import { Scholarships } from './pages/Scholarships'
import { NotFound } from './pages/Planned'
import { Quiz } from './pages/Quiz'
import { MyProgress, RoadmapPage, Roadmaps } from './pages/Roadmaps'
import { Skills } from './pages/Skills'

function Protected({ children, admin = false }: { children: ReactNode; admin?: boolean }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <p className="py-10 text-center text-muted">Loading…</p>
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  if (admin && user.role !== 'admin') return <NotFound />
  return children
}


/** Old area links now open the same area in the step-by-step chooser. */
function AreaRedirect() {
  const { slug = '' } = useParams()
  return <Navigate to={`/choose/${slug}`} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="choose" element={<ChooseArea />} />
            <Route path="choose/:field" element={<ChooseCourse />} />
            <Route path="choose/:field/:course" element={<ChooseCareer />} />
            <Route path="explore" element={<Navigate to="/choose" replace />} />
            <Route path="explore/:slug" element={<AreaRedirect />} />
            <Route path="courses" element={<Navigate to="/all-courses" replace />} />
            <Route path="all-courses" element={<AllCourses />} />
            <Route path="courses/:slug" element={<CourseDetailPage />} />
            <Route path="compare" element={<Compare />} />
            <Route path="compare-careers" element={<CompareCareers />} />
            <Route path="quiz" element={<Quiz />} />
            <Route path="roadmaps" element={<Roadmaps />} />
            <Route path="roadmaps/:slug" element={<RoadmapPage />} />
            <Route path="skills" element={<Skills />} />
            <Route path="dates" element={<DatesPage />} />
            <Route path="updates" element={<UpdatesPage />} />
            <Route path="opportunities" element={<Navigate to="/choose" replace />} />
            <Route path="scholarships" element={<Scholarships />} />
            <Route path="my-path" element={<MyPath />} />
            <Route path="my-course" element={<MyPath />} />
            <Route path="colleges" element={<Colleges />} />
            <Route path="colleges/compare" element={<CollegeCompare />} />
            <Route path="colleges/:id" element={<CollegeDetailPage />} />
            <Route path="assistant" element={<Assistant />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            <Route path="account" element={<Protected><Account /></Protected>} />
            <Route path="my-progress" element={<Protected><MyProgress /></Protected>} />
            <Route path="admin" element={<Protected admin><Admin /></Protected>} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
