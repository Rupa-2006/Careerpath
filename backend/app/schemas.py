import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegionOut(OrmModel):
    id: int
    code: str
    name: str
    kind: str


class SubjectOut(OrmModel):
    id: int
    slug: str
    name: str


class StreamOut(OrmModel):
    id: int
    slug: str
    name: str
    aliases: list[str]
    subjects: list[SubjectOut]


class SourceOut(OrmModel):
    name: str
    url: str
    is_official: bool


class TrustOut(OrmModel):
    status: str
    academic_year: str | None
    last_updated: date | None
    source: SourceOut | None


class FieldSummary(TrustOut):
    slug: str
    name: str
    tagline: str
    course_count: int = 0


class ExamOut(TrustOut):
    slug: str
    name: str
    conducted_by: str
    summary: str
    region: RegionOut | None


class EligibilityResult(BaseModel):
    """`status` is one of: eligible, not_eligible, need_subjects, check, no_rule."""

    status: str
    message: str
    missing: list[str] = []


class SourceWatchOut(OrmModel):
    id: int
    name: str
    url: str
    affects: str
    change_summary: str | None
    last_error: str | None
    last_checked_at: datetime | None
    last_changed_at: datetime | None
    needs_review: bool


class CareerGrowthOut(BaseModel):
    first: str
    next: str
    senior: str
    ready: list[str]


class CareerOpportunityOut(TrustOut):
    kind: str
    title: str
    detail: str
    url: str


class TechChangeOut(TrustOut):
    slug: str
    title: str
    level: str
    what_changed: str
    why_it_matters: str
    learn_next: str


class CourseListingOut(TrustOut):
    name: str
    group_name: str
    duration: str
    state: str
    route: str
    course_slug: str | None


class ScholarshipOut(TrustOut):
    slug: str
    name: str
    run_by: str
    kind: str
    audience: str
    state: str | None
    who_can_apply: str
    what_you_get: str
    how_to_apply: str
    apply_url: str


class CourseSummary(TrustOut):
    slug: str
    name: str
    kind: str
    summary: str
    duration: str
    field_slug: str
    field_name: str
    eligibility: EligibilityResult


class CourseList(BaseModel):
    total: int
    courses: list[CourseSummary]


class FieldDetail(FieldSummary):
    what_is_it: str
    what_you_learn: str
    who_can_choose: str
    required_skills: str
    further_education: str
    courses: list[CourseSummary]


class GroupOut(BaseModel):
    min_count: int
    subjects: list[str]


class CriterionOut(TrustOut):
    label: str
    summary: str
    subjects_known: bool
    min_percentage: float | None
    min_percentage_reserved: float | None
    min_age: int | None
    max_age: int | None
    regions: list[str]
    groups: list[GroupOut]


class CourseDetail(CourseSummary):
    what_you_study: str
    path_note: str = ""
    path_years: int | None = None
    roadmaps: list[dict[str, str]] = []
    admission: str
    careers: list[str]
    exams: list[ExamOut]
    criteria: list[CriterionOut]


class OfferingOut(TrustOut):
    id: int
    course_slug: str
    course_name: str
    branch: str | None


class FactOut(TrustOut):
    id: int
    kind: str
    value: str


class CollegeSummary(TrustOut):
    id: int
    aishe_code: str
    name: str
    region: RegionOut
    district: str | None
    college_type: str | None
    management: str | None
    university_name: str | None


class CollegeList(BaseModel):
    total: int
    page: int
    pages: int
    colleges: list[CollegeSummary]


class CollegeDetail(CollegeSummary):
    year_established: int | None
    location: str | None
    university_type: str | None
    website: str | None
    offerings: list[OfferingOut]
    facts: list[FactOut]


class CollegeFilters(BaseModel):
    districts: list[str]
    college_types: list[str]
    managements: list[str]


class SourcedIn(BaseModel):
    """An admin must say where they read it. Nothing is added from memory."""

    academic_year: str = Field(pattern=r"^20\d\d-\d\d$")
    source_name: str = Field(min_length=3, max_length=200)
    source_url: HttpUrl


class OfferingIn(SourcedIn):
    course_slug: str = Field(max_length=60)
    branch: str | None = Field(default=None, max_length=150)


class FactIn(SourcedIn):
    kind: Literal["fees", "placements", "facilities", "admission"]
    value: str = Field(min_length=3, max_length=2000)


class WebsiteIn(BaseModel):
    website: HttpUrl


class BatchOut(OrmModel):
    id: int
    file_name: str
    status: str
    rows_read: int
    rows_new: int
    rows_changed: int
    rows_unchanged: int
    rows_rejected: int
    rows_missing: int
    problems: list
    created_at: datetime
    source: SourceOut


class RoadmapSummary(TrustOut):
    slug: str
    name: str
    description: str
    step_count: int
    years: int
    courses: list[str]


class StepOut(BaseModel):
    id: int
    year: int
    semester: int
    title: str
    why: str
    build_task: str
    resources: list[str]
    done: bool


class RoadmapDetail(RoadmapSummary):
    uses_semesters: bool
    course_slugs: list[str]
    steps: list[StepOut]
    done_count: int
    next_step_id: int | None


class ProgressRow(BaseModel):
    slug: str
    name: str
    done: int
    total: int
    next_step: str | None
    next_step_id: int | None


class QuizOptionOut(BaseModel):
    id: int
    text: str


class QuizQuestionOut(BaseModel):
    id: int
    text: str
    options: list[QuizOptionOut]


class QuizAnswersIn(BaseModel):
    answers: dict[int, int] = Field(max_length=50)
    stream_id: int | None = None
    region_id: int | None = None
    subject_ids: list[int] = Field(default=[], max_length=30)


class QuizCourseOut(BaseModel):
    slug: str
    name: str
    summary: str
    points: int
    reasons: list[str]
    roadmaps: list[dict[str, str]]


class QuizResultOut(BaseModel):
    answered: int
    results: list[QuizCourseOut]
    also: list[dict[str, str]]
    top_tie: bool


class DateOut(TrustOut):
    id: int
    title: str
    certainty: str
    starts_on: date | None
    ends_on: date | None
    note: str
    checked_on: date
    days_left: int | None
    recheck_due: bool


class DatesOut(BaseModel):
    upcoming: list[DateOut]
    waiting: list[DateOut]


class ReportIn(BaseModel):
    page: str = Field(max_length=200, pattern=r"^/")
    message: str = Field(min_length=3, max_length=1000)
    website: str = Field(default="", max_length=200)   # hidden field that only robots fill in


class ReportOut(OrmModel):
    id: int
    page: str
    message: str
    resolved: bool
    created_at: datetime


class UpdateOut(BaseModel):
    title: str
    link: str
    source_name: str
    why_it_matters: str
    published_at: datetime | None


class UpdatesOut(BaseModel):
    tools: list[UpdateOut]
    latest: list[UpdateOut]
    last_collected: datetime | None


class OpportunitySourceOut(BaseModel):
    name: str
    url: str
    description: str


class SkillOut(TrustOut):
    id: int
    slug: str
    category: str
    name: str
    why: str
    project: str
    resources: list[dict[str, str]]
    for_all: bool
    state: str | None


class SkillStatusIn(BaseModel):
    state: Literal["learning", "done"]


class AssistantIn(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    subject_ids: list[int] = Field(default_factory=list, max_length=20)
    stream_id: int | None = None
    region_id: int | None = None
    lang: Literal["en", "te"] = "en"

    @field_validator("message")
    @classmethod
    def has_words(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Please type a question.")
        return value.strip()


class AssistantCard(TrustOut):
    kind: Literal["course", "field", "exam", "roadmap", "skill", "date"]
    title: str
    to: str | None
    why: str
    detail: str
    eligibility: EligibilityResult | None = None


class AssistantOut(BaseModel):
    intent: str
    text: str
    cards: list[AssistantCard]
    next_questions: list[str]
    used_ai: bool


class ReviewItem(BaseModel):
    entity: str
    id: int
    title: str
    detail: str
    status: str
    source: SourceOut | None
    prechecked: bool = False


class GroupPublishIn(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=5000)
    checked: bool   # the admin ticked "I have checked these against their sources"


class GroupPublishOut(BaseModel):
    published: int
    skipped: int


class ReviewIn(BaseModel):
    status: Literal["pending_verification", "verified", "published", "outdated"]
    note: str | None = Field(default=None, max_length=500)


class UserOut(OrmModel):
    id: uuid.UUID
    email: str
    name: str | None
    role: str
    region_id: int | None
    stream_id: int | None
    path: str = ""   # the career chosen at sign-up; it stays fixed


class SavedStep(BaseModel):
    on: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")   # the day it was finished
    note: str | None = Field(default=None, max_length=300)                    # what the student made


class SavedProgress(BaseModel):
    """Everything My Path keeps. Sizes are capped so an account can't be used to store anything else."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(default="", max_length=80, pattern=r"^[a-z0-9-]*$")
    path_from: str = Field(default="", max_length=200)
    steps: dict[str, SavedStep] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list, max_length=500)

    @field_validator("steps")
    @classmethod
    def check_steps(cls, value: dict[str, SavedStep]) -> dict[str, SavedStep]:
        if len(value) > 2000 or any(not key.isdigit() or len(key) > 9 for key in value):
            raise ValueError("Steps must be step numbers.")
        return value

    @field_validator("skills")
    @classmethod
    def check_skills(cls, value: list[str]) -> list[str]:
        if any(len(item) > 80 or not item.replace("-", "").isalnum() for item in value):
            raise ValueError("Skills must be skill names.")
        return sorted(set(value))


class SavedProgressOut(SavedProgress):
    saved_at: datetime | None = None


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=1000)
    name: str | None = Field(default=None, max_length=100)
    path: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")   # the career, chosen once at sign-up

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return (value or "").strip() or None


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=1000)


class ProfileIn(BaseModel):
    """Only fields that were sent are changed. Sending null clears a field."""

    name: str | None = Field(default=None, max_length=100)
    region_id: int | None = None
    stream_id: int | None = None


class PasswordChangeIn(BaseModel):
    current_password: str = Field(max_length=1000)
    new_password: str = Field(max_length=1000)


class DeleteAccountIn(BaseModel):
    password: str = Field(max_length=1000)


class AdminUserOut(OrmModel):
    id: uuid.UUID
    email: str
    name: str | None
    role: str
    is_active: bool
    created_at: datetime


class AdminUserList(BaseModel):
    total: int
    users: list[AdminUserOut]


class AdminUserIn(BaseModel):
    role: Literal["student", "admin"] | None = None
    is_active: bool | None = None


class AdminSummary(BaseModel):
    students: int
    admins: int
    regions: int
    streams: int
    sources: int
    pending_verification: int
