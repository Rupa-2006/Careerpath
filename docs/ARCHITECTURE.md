# CareerPath architecture

CareerPath helps students discover what they can do after Intermediate, then follow a path to it. It is built first for Andhra Pradesh and Telangana. National exams such as JEE Main and NEET are covered, and rules are stored by state, so more states can be added later without a rewrite.
This document records the decisions behind the build. The database is in [DATABASE.md](DATABASE.md).

## 1. The hard problems

| Challenge | Why it is hard | Decision |
|---|---|---|
| Trust | A wrong eligibility rule can cost a student a year | Every record carries a source and a status. Students only see published records. AI never supplies admission facts |
| All-India scale | Over 45,000 colleges, with rules that differ by state | The database holds rules as data, so a new state or course needs no code change |
| "Automatic" updates | Most official bodies publish PDFs and pages, not APIs | Automate what has an authorised feed. Queue the rest for review. Never claim an integration that does not exist |
| Eligibility | "Who can join?" depends on subjects and state, not only on stream | Eligibility is stored per subject and per state, not as a stream label |
| Personal roadmaps | Every course, branch and goal needs its own plan | Roadmaps are built from reusable steps, filtered by course, branch and goal |
| Low-cost phones and data | Most students use budget phones | Small pages, mobile first, no heavy libraries |

## 2. System design

```
 Student's browser
       |
 React + TypeScript + Tailwind         one app, served as static files
       |  /api/v1, session cookie
 FastAPI                               validation, auth, roles, rate limits
   |            |              |
 PostgreSQL   Gemini API     Background jobs (from Phase 6)
              (Phase 5,      RSS and official sources -> staging tables
               server only)  -> validation -> admin review -> published tables
```

### Main decisions
| Decision | Choice | Why |
|---|---|---|
| Login | Random session token in an `HttpOnly` cookie, stored hashed in the database | JavaScript can't read it, so an XSS bug can't steal it. Sessions can be cancelled at once, which JWTs can't do simply |
| Password hashing | Argon2id | Current best practice |
| CSRF | `SameSite=Lax` cookie, plus an Origin check and a required custom header on every change | Blocks forged requests from other sites |
| Rate limits | Counted in PostgreSQL | Works across server processes and restarts, with no Redis needed yet |
| Background jobs | APScheduler first | One process is enough at this size. Celery needs Redis and more hosting cost, so move only if job volume requires it |
| AI key | Server only | Never reaches the browser |
| Languages | English only for now. The translations table and frontend text pairs stay, unused, in case a language is added later | Adding a language needs no table changes |

## 3. Publishing pipeline

Nothing automated goes straight to students.

```
collected  ->  staging record  ->  automatic checks  ->  review  ->  published
(job)          (raw + source)      (duplicates,          (admin)
                                    changes, format)
```

Statuses: `unverified`, `pending_verification`, `verified`, `published`, `outdated`.
The API serves students `published` records only. A record becomes `outdated` by itself when its academic year passes or its review date expires.

Low-risk items such as news headlines can publish automatically, labelled as news. Admission rules, fees and eligibility always need a person.

## 4. What can and cannot be automated

Findings as of November 2026. Each source must be re-checked before its phase starts.

| Data | Source | Automation | Status |
|---|---|---|---|
| States and UTs | Fixed list | Not needed | Done in Phase 1 |
| College names and locations | [All Colleges as per AISHE Dashboard](https://aikosh.indiaai.gov.in/home/datasets/details/all_colleges_as_per_aishe_dashboard_3.html) on AIKosh, under the Open Government License | Semi-automatic: download the file, run the importer, approve the batch. The file has no website, course, fee or placement columns | Built in Phase 3. No confirmed API, so a person starts each import |
| Branches and intake | Regulators such as AICTE | Unknown. No API or dataset found yet | To research. Do not assume |
| Fees, placements, facilities | Each college's own website | **Not automatable.** Formats differ, and scraping may break site terms | Show only when verified, otherwise "not available" |
| Eligibility and exam rules | Exam notices, mostly PDFs | **Change detection only:** alert an admin that a page changed, then a person reads it | Phase 7 |
| Technology news | Publishers' RSS feeds | Yes, headlines and links | Phase 6 |
| AI summaries | Gemini | Yes, labelled as AI summaries, with a link to the original | Phase 6 |
| Internships and jobs | Portals | Only with an authorised feed or API. None confirmed yet | Admin-entered links until then |

A college adding a branch can only be detected automatically if an official feed reports it. Without one, the change reaches the database through review or a student's report.

The [data.gov.in listing](https://www.data.gov.in/resource/list-all-universities-2011-2012) checked so far is from 2011-12 and has no API. No API is assumed in this project.

## 5. API plan

All routes start with `/api/v1`. Phase 1 and 2 routes are working now, plus `GET /admin/review` and `POST /admin/review/{entity}/{id}`, brought forward from Phase 7 so content can be published.

| Phase | Routes |
|---|---|
| 1 | `GET /health`, `GET /reference/states`, `GET /reference/streams`, `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `PATCH /me`, `POST /me/password`, `DELETE /me`, `GET /admin/summary`, `GET /admin/users`, `PATCH /admin/users/{id}` |
| 2 | `GET /fields`, `GET /fields/{slug}`, `GET /courses`, `GET /courses/{slug}`, `GET /courses/compare`, `GET /exams` |
| 3 | `GET /colleges`, `GET /colleges/{id}`, `GET /colleges/compare` |
| 4 | `GET /roadmaps`, `GET /roadmaps/{slug}`, `GET /skills`, `PUT /me/progress/{step}`, `PUT /me/skills/{skill}` |
| 5 | `POST /assistant/messages` |
| 6 | `GET /updates` |
| 7 | `GET /admin/review-queue`, `POST /admin/review-queue/{id}/approve`, `POST /admin/review-queue/{id}/reject`, `GET /admin/jobs` |
| 8 | `GET /opportunities` |

## 6. Folder structure

```
CareerPath/
  backend/
    app/
      api/          one file per feature
      models/       database tables
      schemas/      request and response shapes
      core/         settings, security, database, middleware
    alembic/        database migrations
    scripts/        dev database, reference data, admin creation
    tests/
  frontend/
    src/
      api/          the only code that calls the backend
      components/   reusable pieces
      context/      logged-in user
      pages/        one file per page
      data/         text that moves to the database in Phase 2
  docs/
```

## 7. AI assistant rules (Phase 5)

The Career Assistant (`backend/app/assistant.py`) builds every answer from published records and the eligibility rules. It needs no AI account and cannot invent a course, a rule or a date.

- It only suggests paths the student's subjects allow, and says what it left out and why.
- It explains why, shows more than one option, and links the source. It never picks for the student.
- It never promises admission or jobs. It has no salary, fee or cutoff data, and says so.
- If the records have no answer, it says so.
- A message about self-harm gets the Tele-MANAS helpline (14416 or 1-800-891-4416) and 112, and never reaches an AI service.
- Nothing a student types is saved. The chat lives only in the open page.
- It understands English questions by matching words, so it is not a free conversation partner. Replies are in English only for now.

**Why Gemini is off.** The [Gemini API terms](https://ai.google.dev/gemini-api/terms) (effective March 23, 2026) require users to be 18 or older, and forbid using the service in a website "likely to be accessed by individuals under the age of 18". CareerPath is for students, many of them 16 or 17. On the unpaid tier, Google may also use what is sent to improve its products, and human reviewers may read it. So `assistant_ai_on` in `core/config.py` is always false in production. Don't remove that check unless the terms change or another provider's terms have been read and allow it.

**Trying the AI wording on this computer.** Add `ASSISTANT_AI=true` and `GEMINI_API_KEY=...` to `backend/.env`, then restart the API. `backend/app/assistant_ai.py` only rewords a finished answer. The cards always come from the database, emails and phone numbers are removed first, and wording with a new number, a link or a promise is thrown away. The call follows Google's documented `generateContent` format but has not been run against the live service, because no key was available. Google now recommends its newer Interactions API for new projects. The model name, `gemini-3.5-flash-lite`, came from Google's [models page](https://ai.google.dev/gemini-api/docs/models) in November 2026.

## 8. Roadmap

| Phase | Delivers | Needs from you |
|---|---|---|
| **1. Foundation (done)** | App, database, accounts, roles, admin basics | Nothing |
| **2. Courses (done)** | Fields, courses, exams, eligibility by subject and state, review queue | Review and publish the records |
| **3. Colleges (done)** | Directory from official data, safe importer, comparisons, sourced details | Download the official file |
| 4. Roadmaps and skills | Roadmaps, progress and the skill checklist are done. Personal filtering by branch remains | Content review |
| **5. Assistant (done)** | Career Assistant from reviewed records, with optional AI wording off by default | Review and publish the records |
| 6. Tech updates | Scheduled feeds, AI summaries | Choice of feeds |
| 7. Data engine | Review queue, change detection, job monitoring | Weekly reviews |
| 8. Internships and jobs | Listings with deadlines | Authorised sources |
| 9. Launch | Security review, hosting, documentation | Paid hosting |

**Hosting:** PythonAnywhere's free plan does not suit this stack, because the app needs PostgreSQL and background jobs. Expect to use a hosted PostgreSQL service plus an app host, and compare current prices at Phase 9.

**Realistic scope:** this is a very large product. Full all-India eligibility data for every state is a long-term content effort. The honest plan is to build the full system, then widen coverage state by state, showing clearly what is covered.
