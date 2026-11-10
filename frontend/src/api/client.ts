export type User = {
  id: string
  username: string
  path: string   // the career chosen at sign-up; fixed
  email: string
  name: string | null
  role: 'student' | 'admin'
  region_id: number | null
  stream_id: number | null
}

/** My Path progress kept with an account. Steps are keyed by step id. */
export type SavedProgress = {
  path: string
  path_from: string
  steps: Record<string, { on?: string; note?: string }>
  skills: string[]
  diary?: DiaryEntry[]
  saved_at?: string | null
}
/** One diary entry. Private to the student. "deleted" lets other devices remove it too. */
export type DiaryEntry = {
  id: string; on: string; at: string; did: string; learned: string; next: string; step?: number | null; deleted?: boolean
}
export type PathChangeRequest = {
  id: number; from_path: string; from_name: string; to_path: string; to_name: string; reason: string
  status: 'pending' | 'approved' | 'rejected'; created_at: string; decided_at: string | null
  student_email: string | null; student_name: string | null
}
export type PathChangeStatus = { path: string; free_left: number; latest: PathChangeRequest | null; next_change_on: string | null }
export type Region = { id: number; code: string; name: string; kind: 'state' | 'union_territory' }
export type Stream = { id: number; slug: string; name: string; aliases: string[]; subjects: { id: number; name: string }[] }

export type Source = { name: string; url: string; is_official: boolean }
export type Trust = { status: string; academic_year: string | null; last_updated: string | null; source: Source | null }
export type Eligibility = {
  status: 'eligible' | 'not_eligible' | 'need_subjects' | 'check' | 'no_rule'
  message: string
  missing: string[]
}
export type FieldSummary = Trust & { slug: string; name: string; tagline: string; course_count: number }
export type CourseSummary = Trust & {
  slug: string
  name: string
  kind: string
  summary: string
  duration: string
  field_slug: string
  field_name: string
  eligibility: Eligibility
}
export type FieldDetail = FieldSummary & {
  what_is_it: string
  what_you_learn: string
  who_can_choose: string
  required_skills: string
  further_education: string
  courses: CourseSummary[]
}
export type Exam = Trust & { slug: string; name: string; conducted_by: string; summary: string; region: Region | null }
export type Criterion = Trust & {
  label: string
  summary: string
  subjects_known: boolean
  min_percentage: number | null
  min_percentage_reserved: number | null
  min_age: number | null
  max_age: number | null
  regions: string[]
  groups: { min_count: number; subjects: string[] }[]
}
export type CourseDetail = CourseSummary & {
  what_you_study: string
  path_note: string
  path_years: number | null
  roadmaps: { slug: string; name: string }[]
  admission: string
  careers: string[]
  exams: Exam[]
  criteria: Criterion[]
}
export type ReviewItem = { entity: string; id: number; title: string; detail: string; status: string; source: Source | null; prechecked: boolean }
export type Subject = { id: number; slug: string; name: string }

export type CollegeSummary = Trust & {
  id: number
  aishe_code: string
  name: string
  region: Region
  district: string | null
  college_type: string | null
  management: string | null
  university_name: string | null
}
export type Offering = Trust & { id: number; course_slug: string; course_name: string; branch: string | null }
export type Fact = Trust & { id: number; kind: 'fees' | 'placements' | 'facilities' | 'admission'; value: string }
export type CollegeDetail = CollegeSummary & {
  year_established: number | null
  location: string | null
  university_type: string | null
  website: string | null
  offerings: Offering[]
  facts: Fact[]
}
export type CollegeFilters = { districts: string[]; college_types: string[]; managements: string[] }
export type ImportBatch = {
  id: number
  file_name: string
  status: 'pending' | 'published' | 'rejected'
  rows_read: number
  rows_new: number
  rows_changed: number
  rows_unchanged: number
  rows_rejected: number
  rows_missing: number
  problems: string[]
  created_at: string
  source: Source
}
export type SourcedInput = { academic_year: string; source_name: string; source_url: string }

export type RoadmapSummary = Trust & { slug: string; name: string; description: string; step_count: number; years: number; courses: string[] }
export type RoadmapStep = { id: number; year: number; semester: number; title: string; why: string; build_task: string; resources: string[]; done: boolean }
export type RoadmapDetail = RoadmapSummary & {
  uses_semesters: boolean
  course_slugs: string[]
  steps: RoadmapStep[]
  done_count: number
  next_step_id: number | null
}
export type ProgressRow = { slug: string; name: string; done: number; total: number; next_step: string | null; next_step_id: number | null }
export type QuizQuestion = { id: number; text: string; options: { id: number; text: string }[] }
export type QuizResult = {
  answered: number
  top_tie: boolean
  also: { slug: string; name: string }[]
  results: { slug: string; name: string; summary: string; points: number; reasons: string[]; roadmaps: { slug: string; name: string }[] }[]
}
export type ImportantDate = Trust & {
  id: number
  title: string
  certainty: 'CONFIRMED' | 'REPORTED' | 'NOT_ANNOUNCED'
  starts_on: string | null
  ends_on: string | null
  note: string
  checked_on: string
  days_left: number | null
  recheck_due: boolean
}
export type Dates = { upcoming: ImportantDate[]; waiting: ImportantDate[] }
export type UpdateItem = { title: string; link: string; source_name: string; why_it_matters: string; published_at: string | null }
export type Updates = { tools: UpdateItem[]; latest: UpdateItem[]; last_collected: string | null }
export type SourceWatch = { id: number; name: string; url: string; affects: string; change_summary: string | null; last_error: string | null; last_checked_at: string | null; last_changed_at: string | null; needs_review: boolean }
export type CareerGrowth = { first: string; next: string; senior: string; ready: string[] }
export type CareerOpportunity = Trust & { kind: string; title: string; detail: string; url: string }
export type TechChange = Trust & { slug: string; title: string; level: string; what_changed: string; why_it_matters: string; learn_next: string }
export type CourseListing = Trust & { name: string; group_name: string; duration: string; state: string; route: string; course_slug: string | null }
export type Scholarship = Trust & {
  slug: string; name: string; run_by: string; kind: string; audience: string; state: string | null
  who_can_apply: string; what_you_get: string; how_to_apply: string; apply_url: string
}
export type OpportunitySource = { name: string; url: string; description: string }
export type ReportItem = { id: number; page: string; message: string; resolved: boolean; created_at: string }

export type Skill = Trust & {
  id: number
  slug: string
  category: string
  name: string
  why: string
  project: string
  resources: { label: string; url: string }[]
  for_all: boolean
  state: 'learning' | 'done' | null
}

export type AssistantCard = Trust & {
  kind: 'course' | 'field' | 'exam' | 'roadmap' | 'skill' | 'date'
  title: string
  to: string | null
  why: string
  detail: string
  eligibility: Eligibility | null
}
export type AssistantReply = { intent: string; text: string; cards: AssistantCard[]; next_questions: string[]; used_ai: boolean }
export type AssistantQuestion = { message: string; subject_ids: number[]; stream_id: number | null; region_id: number | null; lang: string }

export type AdminUser = {
  id: string
  username: string
  email: string
  name: string | null
  role: User['role']
  is_active: boolean
  created_at: string
}
export type AdminSummary = {
  students: number
  admins: number
  regions: number
  streams: number
  sources: number
  pending_verification: number
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api/v1${path}`, {
      method,
      credentials: 'same-origin',
      headers: {
        'X-CareerPath-Client': 'web',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, "We can't reach the server. Check your connection and try again.")
  }

  if (response.status === 204) return undefined as T
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string' ? detail : 'Please check what you entered and try again.'
    throw new ApiError(response.status, response.status >= 500 ? 'Something went wrong on our side. Please try again.' : message)
  }
  return data as T
}

export const api = {
  me: () => request<User>('/auth/me'),
  savedProgress: () => request<SavedProgress>('/me/saved-progress'),
  pathChange: () => request<PathChangeStatus>('/me/path-change'),
  changePath: (path: string, reason: string) =>
    request<{ result: 'changed' | 'requested'; message: string }>('/me/path-change', 'POST', { path, reason }),
  pathRequests: () => request<PathChangeRequest[]>('/admin/path-requests'),
  decidePathRequest: (id: number, approve: boolean) => request<PathChangeRequest>(`/admin/path-requests/${id}`, 'POST', { approve }),
  saveProgress: (data: SavedProgress) => request<SavedProgress>('/me/saved-progress', 'PUT', data),
  register: (username: string, email: string, password: string, name: string, path: string) =>
    request<User>('/auth/register', 'POST', { username, email, password, name, path }),
  login: (login: string, password: string) => request<User>('/auth/login', 'POST', { login, password }),
  forgotPassword: (email: string) => request<{ message: string }>('/auth/forgot-password', 'POST', { email }),
  resetPassword: (email: string, code: string, new_password: string) =>
    request<{ message: string }>('/auth/reset-password', 'POST', { email, code, new_password }),
  forgotUsername: (email: string) => request<{ message: string }>('/auth/forgot-username', 'POST', { email }),
  logout: () => request<void>('/auth/logout', 'POST'),
  updateProfile: (changes: Partial<Pick<User, 'name' | 'region_id' | 'stream_id'>>) =>
    request<User>('/me', 'PATCH', changes),
  changePassword: (current_password: string, new_password: string) =>
    request<void>('/me/password', 'POST', { current_password, new_password }),
  deleteAccount: (password: string) => request<void>('/me', 'DELETE', { password }),
  states: () => request<Region[]>('/reference/states'),
  streams: () => request<Stream[]>('/reference/streams'),
  subjects: () => request<Subject[]>('/reference/subjects'),
  fields: () => request<FieldSummary[]>('/fields'),
  field: (slug: string, query: string) => request<FieldDetail>(`/fields/${slug}?${query}`),
  courses: (query: string) => request<{ total: number; courses: CourseSummary[] }>(`/courses?${query}`),
  course: (slug: string, query: string) => request<CourseDetail>(`/courses/${slug}?${query}`),
  compare: (slugs: string[], query: string) =>
    request<CourseDetail[]>(`/courses/compare?slugs=${encodeURIComponent(slugs.join(','))}&${query}`),
  colleges: (query: string) =>
    request<{ total: number; page: number; pages: number; colleges: CollegeSummary[] }>(`/colleges?${query}`),
  collegeFilters: (region: number | null) => request<CollegeFilters>(`/colleges/filters${region ? `?region=${region}` : ''}`),
  college: (id: string) => request<CollegeDetail>(`/colleges/${id}`),
  compareColleges: (ids: string[]) => request<CollegeDetail[]>(`/colleges/compare?ids=${ids.join(',')}`),
  imports: () => request<ImportBatch[]>('/admin/imports'),
  publishImport: (id: number, allowLargeRemoval: boolean) =>
    request<ImportBatch>(`/admin/imports/${id}/publish?allow_large_removal=${allowLargeRemoval}`, 'POST'),
  rejectImport: (id: number) => request<ImportBatch>(`/admin/imports/${id}/reject`, 'POST'),
  addOffering: (id: number, data: SourcedInput & { course_slug: string; branch: string }) =>
    request<Offering>(`/admin/colleges/${id}/offerings`, 'POST', data),
  addFact: (id: number, data: SourcedInput & { kind: string; value: string }) =>
    request<Fact>(`/admin/colleges/${id}/facts`, 'POST', data),
  setWebsite: (id: number, website: string) => request<CollegeDetail>(`/admin/colleges/${id}/website`, 'PATCH', { website }),
  deleteOffering: (id: number) => request<void>(`/admin/colleges/offerings/${id}`, 'DELETE'),
  deleteFact: (id: number) => request<void>(`/admin/colleges/facts/${id}`, 'DELETE'),
  roadmaps: (lang: string) => request<RoadmapSummary[]>(`/roadmaps?lang=${lang}`),
  roadmap: (slug: string, lang: string) => request<RoadmapDetail>(`/roadmaps/${slug}?lang=${lang}`),
  markStep: (id: number) => request<void>(`/me/progress/${id}`, 'PUT'),
  unmarkStep: (id: number) => request<void>(`/me/progress/${id}`, 'DELETE'),
  myProgress: (lang: string) => request<ProgressRow[]>(`/me/progress?lang=${lang}`),
  quiz: (lang: string) => request<QuizQuestion[]>(`/quiz?lang=${lang}`),
  scoreQuiz: (data: { answers: Record<number, number>; stream_id?: number | null; region_id?: number | null; subject_ids?: number[] }, lang: string) =>
    request<QuizResult>(`/quiz/score?lang=${lang}`, 'POST', data),
  myQuizResult: (lang: string) => request<QuizResult | null>(`/me/quiz-result?lang=${lang}`),
  dates: (lang: string, stream: number | null) => request<Dates>(`/dates?lang=${lang}${stream ? `&stream=${stream}` : ''}`),
  courseDates: (course: string) => request<Dates>(`/dates?lang=en&course=${course}`),
  updates: (lang: string) => request<Updates>(`/updates?lang=${lang}`),
  careerGrowth: (roadmap: string) => request<CareerGrowth | null>(`/career-growth?roadmap=${roadmap}`),
  careerOpportunities: (roadmap: string) => request<CareerOpportunity[]>(`/career-opportunities?roadmap=${roadmap}`),
  careerUpdates: (roadmap: string) => request<UpdateItem[]>(`/updates/career?roadmap=${roadmap}`),
  techChanges: (roadmap: string) => request<TechChange[]>(`/technology-changes${roadmap ? `?roadmap=${roadmap}` : ''}`),
  courseList: () => request<CourseListing[]>('/course-list'),
  scholarships: () => request<Scholarship[]>('/scholarships'),
  opportunitySources: (lang: string) => request<OpportunitySource[]>(`/opportunities/sources?lang=${lang}`),
  report: (page: string, message: string, website: string) => request<void>('/reports', 'POST', { page, message, website }),
  adminReports: () => request<ReportItem[]>('/admin/reports'),
  resolveReport: (id: number) => request<ReportItem>(`/admin/reports/${id}/resolve`, 'POST'),
  askAssistant: (question: AssistantQuestion) => request<AssistantReply>('/assistant/messages', 'POST', question),
  skills: (lang: string, roadmap: string) =>
    request<Skill[]>(`/skills?lang=${lang}${roadmap ? `&roadmap=${roadmap}` : ''}`),
  setSkill: (id: number, state: 'learning' | 'done') => request<void>(`/me/skills/${id}`, 'PUT', { state }),
  clearSkill: (id: number) => request<void>(`/me/skills/${id}`, 'DELETE'),
  watches: () => request<SourceWatch[]>('/admin/watches'),
  watchReviewed: (id: number) => request<SourceWatch>(`/admin/watches/${id}/reviewed`, 'POST'),
  reviewQueue: (status: string) => request<ReviewItem[]>(`/admin/review?status=${status}`),
  publishGroup: (entity: string, ids: number[]) =>
    request<{ published: number; skipped: number }>(`/admin/review-group/${entity}`, 'POST', { ids, checked: true }),
  review: (entity: string, id: number, status: string) =>
    request<ReviewItem>(`/admin/review/${entity}/${id}`, 'POST', { status }),
  adminSummary: () => request<AdminSummary>('/admin/summary'),
  adminUsers: (query: string) =>
    request<{ total: number; users: AdminUser[] }>(`/admin/users?q=${encodeURIComponent(query)}`),
  adminUpdateUser: (id: string, changes: { is_active?: boolean; role?: User['role'] }) =>
    request<AdminUser>(`/admin/users/${id}`, 'PATCH', changes),
}
