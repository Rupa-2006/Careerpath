# CareerPath: Discover Your Future

A platform to help students discover, compare and choose what to do after Intermediate. It is built first for Andhra Pradesh and Telangana, and its design lets more states be added later.

CareerPath is the full version of this product. It absorbs Stepora, the first version, whose content lives in `backend/scripts/stepora/`.

**Status: Phases 1 to 3 and 5 of 9, plus most of Phase 4.** Accounts, fields, courses, eligibility, colleges, the quiz, roadmaps with progress, skills, the Career Assistant, exam dates, reports and tech headlines work. The assistant answers from reviewed records, with no AI service switched on (see docs/ARCHITECTURE.md, section 7). Pages for later phases say so openly, and nothing shows invented data.

- [Architecture, data sources and roadmap](docs/ARCHITECTURE.md)
- [Database design](docs/DATABASE.md)

## Quick start

Double-click `Start CareerPath.bat`. keep the small CareerPath windows open while you use the site.

## What works now
- Sign up, log in, log out, and sessions that can be cancelled
- Profile with State or UT and Class 12 stream, change password, delete account
- All 28 States and 8 Union Territories, and common Class 12 streams
- Admin area: real counts, user search, deactivate and reactivate
- Rate limits, forged-request protection and security headers
- 18 fields explained, and a searchable course explorer with comparison
- Eligibility checks by Class 12 subjects and State
- Review queue: nothing reaches students until an admin publishes it
- College explorer with search, filters and comparison, using only official data
- Find My Path quiz, using each student's subjects to rule out courses that don't fit
- 12 roadmaps with 103 steps, with progress tracking
- Exam dates with trust labels, where past dates disappear by themselves
- Report a mistake, technology headlines, and trusted job websites
- Skill checklist: 26 skills with projects and learning links, filtered by career
- English only. The user dropped Telugu on 2026-11-05; the older Telugu text stays unused in the database and `Language.tsx`

## Run it on Windows
You need Python 3.12 and Node 20 or newer. PostgreSQL is included for development.

### First time
```
cd C:\Projects\CareerPath\backend
py -3.12 -m venv venv
venv\Scripts\python -m pip install -r requirements-dev.txt
copy .env.example .env
venv\Scripts\python -m scripts.dev_db start
venv\Scripts\python -m alembic upgrade head
venv\Scripts\python -m scripts.seed_reference
venv\Scripts\python -m scripts.seed_content
venv\Scripts\python -m scripts.seed_journey
venv\Scripts\python -m scripts.seed_skills
venv\Scripts\python -m scripts.seed_scholarships
venv\Scripts\python -m scripts.seed_course_list
venv\Scripts\python -m scripts.seed_tech_changes
venv\Scripts\python -m scripts.seed_opportunities
venv\Scripts\python -m scripts.seed_prechecks
venv\Scripts\python -m scripts.fetch_updates
venv\Scripts\python -m scripts.create_admin
cd ..\frontend
npm install
```

If Python says a file was blocked by an Application Control policy, Windows is refusing SQLAlchemy's compiled file. Install its official pure-Python build:
```
set DISABLE_SQLALCHEMY_CEXT=1
venv\Scripts\python -m pip install --no-binary sqlalchemy --force-reinstall --no-deps sqlalchemy
```

### Every time
Double-click `start.bat`, or run these in two windows:
```
cd C:\Projects\CareerPath\backend
venv\Scripts\python -m scripts.dev_db start
venv\Scripts\python -m uvicorn app.main:app --port 8001
```
```
cd C:\Projects\CareerPath\frontend
npm run dev
```
Open http://localhost:5173. Developer API docs are at http://127.0.0.1:8001/api/docs.

## Reviewing content
All starter content loads as **awaiting review**. On your laptop `SHOW_UNPUBLISHED=true` shows it with that label, so you can see the site. In production this setting is ignored, and students only see published records.

Log in as admin, open **Admin**, check each record's source, and press **Publish**. A record can't be published without a source. Rules must be published as well as their course, or the site says it has no confirmed rule.

## Loading real colleges
No colleges ship with this project. They come from the Ministry of Education's open data:

1. Download **All Colleges AISHE Dashboard.xlsx** from [AIKosh](https://aikosh.indiaai.gov.in/home/datasets/details/all_colleges_as_per_aishe_dashboard_3.html).
2. Run this, using your file's path:
```
cd C:\Projects\CareerPath\backend
venv\Scripts\python -m scripts.import_colleges "C:\Users\you\Downloads\All Colleges AISHE Dashboard.xlsx"
```
3. Open **Admin**, check the counts and any rejected rows, then press **Publish this import**.

To update later, download the newer file and repeat. The site shows what is new, changed and missing before you approve. Colleges missing from a newer file are marked out of date, never deleted, and details added by admins are kept.

The data's licence requires attribution, which appears on the college pages. Keep it there.

## Keeping it true
| How often | Do this | If you forget |
|---|---|---|
| Every week | Update exam dates in the database and their `checked_on` date, then read reports in **Admin** | Past dates vanish, and after 30 days a date warns it hasn't been re-checked |
| Every 2 weeks | `venv\Scripts\python -m scripts.check_links` | Broken links stay until someone reports them |
| Every day if you can | `venv\Scripts\python -m scripts.fetch_updates` | Headlines over 45 days old are hidden |

A date may only be marked `CONFIRMED` after you read it on the official website.

## Tests
```
cd C:\Projects\CareerPath\backend
venv\Scripts\python -m pytest
```
Tests use their own temporary PostgreSQL server.

## Deploying
Phase 9 will choose the host. The app needs:

1. A hosted PostgreSQL database.
2. `cd frontend && npm run build`. FastAPI then serves the built site, so one server does both.
3. These environment variables:

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` (turns on secure cookies and HSTS, hides the API docs) |
| `DATABASE_URL` | `postgresql+psycopg://user:password@host/database` |
| `ALLOWED_ORIGINS` | Your site address, such as `https://example.com` |

4. `alembic upgrade head`, `python -m scripts.seed_reference`, `python -m scripts.seed_content`, `python -m scripts.seed_journey`, `python -m scripts.seed_skills`, `python -m scripts.create_admin`.
5. Start it with `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers`.

Install `requirements.txt` in production, not `requirements-dev.txt`.
