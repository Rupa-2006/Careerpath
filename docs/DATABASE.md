# CareerPath database design

PostgreSQL. Primary keys are integers, except `users`, which uses UUIDs so account IDs can't be guessed.
Each phase adds its tables through a new migration in `backend/alembic/versions/`.

## Phase 1 tables (built)
| Table | Purpose | Key rules |
|---|---|---|
| `regions` | States and Union Territories | `code` unique; `kind` is `state` or `union_territory` |
| `streams` | Class 12 stream groups | `slug` unique; `aliases` holds local names such as MPC |
| `subjects` | Class 12 subjects | `slug` unique |
| `stream_subjects` | Which subjects a stream usually has | Composite primary key |
| `users` | Accounts | Lower-case `email` unique; `role` is `student` or `admin` |
| `sessions` | Logged-in devices | Only a hash of the token is stored; `expires_at` indexed |
| `rate_limit_events` | Failed logins and sign-ups | Index on `key, created_at` |
| `sources` | Where information came from | `url` unique; `is_official` flag |
| `verification_records` | Every status change, by whom and why | Points to any record by `entity_type` and `entity_id` |
| `update_history` | Log of changes to data | Old and new values as JSON |

## Trust fields
Every table holding facts students rely on gets these columns:

| Column | Meaning |
|---|---|
| `source_id` | Link to `sources` |
| `academic_year` | For example `2026-27` |
| `last_updated` | When the source was last checked |
| `status` | `unverified`, `pending_verification`, `verified`, `published`, `outdated` |

## Phase 2 tables (built)
| Table | Purpose |
|---|---|
| `fields` | Broad areas such as Law, explained in simple language |
| `courses` | A course, with its field, duration and how admission works |
| `eligibility_criteria` | One route into a course. A course can have several, such as NDA's wings |
| `eligibility_groups`, `eligibility_group_subjects` | "At least N of these subjects". Every group of a rule must be met |
| `eligibility_regions` | States a rule applies to; none means all India |
| `entrance_exams`, `course_exams` | Exams and the courses that use them |
| `career_paths`, `course_careers` | Careers and the courses leading to them |

This shape handles every rule found so far: Physics AND Maths AND (Chemistry OR Biology) is three groups, and IISER's "3 of 4 subjects" is one group with `min_count = 3`.

`subjects_known = false` means a rule exists but its subjects are unconfirmed, so the site says "check" and never gives a yes or no.

## Phase 3 tables (built)
| Table | Purpose |
|---|---|
| `import_batches` | One official file: its counts, problems, and who approved it |
| `college_staging` | Collected rows waiting for review. Students can never see this table |
| `colleges` | Real institutions from the official directory, keyed by AISHE code |
| `branches` | Specialisations inside a course |
| `college_courses` | A course a college offers. Added by an admin, with a source |
| `college_facts` | Fees, placements, facilities or admission details, with a source and year |

`college_facts` replaces the separate fee and placement tables planned earlier. Formats differ so much between colleges that one sourced text record is more honest than invented structure. If an official dataset ever provides structured figures, it can get its own table.

## Merged from Stepora (built)
| Table | Purpose |
|---|---|
| `translations` | Telugu and future languages for any record, one row per field |
| `roadmaps`, `roadmap_steps`, `roadmap_courses` | Year-wise plans. Steps are matched by place, so reloading content never loses progress |
| `user_step_progress` | A student's finished steps |
| `quiz_questions`, `quiz_options`, `quiz_option_courses`, `quiz_results` | The quiz. Saved results are snapshots |
| `important_dates`, `important_date_courses` | Exam dates with `certainty`: confirmed, reported or not announced |
| `reports` | Mistakes reported by visitors. No personal details |
| `technology_updates` | Useful tools and collected headlines |
| `opportunity_sources` | Trusted job websites |

## Skills (built)
| Table | Purpose |
|---|---|
| `skills` | A skill, why it matters, and a small project. Linked to no roadmaps means it helps in every career |
| `scholarships` | A scholarship, loan or official portal, with who can apply, what you get and how to apply. Reviewed like other records |
| `career_opportunities` | What opens up after a roadmap: jobs, internships, study, government routes and own work. No salaries or guarantees |
| `source_watches` | An official page checked for changes. A change alerts the admin and never edits student content |
| `tech_changes` | A real technology change with its level, reason, source and the roadmaps it affects. Reviewed like other records |
| `course_listings` | One line in the full course list: name, type, length, state, route and source. Reviewed like other records |
| `prechecks` | Marks a record Claude compared with its official source. An edit to the text clears the mark. It never publishes |
| `skill_roadmaps` | Which careers a skill belongs to |
| `learning_resources` | Where to learn it |
| `user_skills` | A student's checklist: `learning` or `done` |

## Later tables (planned)
| Phase | Table | Purpose |
|---|---|---|
| 5 | None | The assistant saves no chats, so it needs no tables |
| 6 | `update_topics` | Topics, plus AI summary columns on `technology_updates` |
| 7 | `staging_records` | Collected data waiting for review |
| 7 | `collector_jobs`, `collector_runs` | Job set-up, results and failures |
| 8 | `opportunities` | Internships, jobs, apprenticeships, with deadlines |

## Why eligibility has its own tables
A stream label can't answer "can I join?". For example, a course may need Physics, Chemistry and Maths with 45%, while another state sets a different rule. Storing subjects, marks and regions as rows lets the app compare them with a student's real subjects. New rules become data, not code.
