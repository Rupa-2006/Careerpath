import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.core.database import Base

ROLES = ("student", "admin")
VERIFICATION_STATUSES = ("unverified", "pending_verification", "verified", "published", "outdated")


def _in(column: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------- Reference data ----------

class Region(Base):
    """A State or Union Territory. New ones are rows, not code."""

    __tablename__ = "regions"
    __table_args__ = (CheckConstraint(_in("kind", ("state", "union_territory")), name="kind"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(5), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    kind: Mapped[str] = mapped_column(String(20))


stream_subjects = Table(
    "stream_subjects",
    Base.metadata,
    Column("stream_id", ForeignKey("streams.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
)


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))


class Stream(Base):
    """A common group of Class 12 subjects. Eligibility rules will use subjects, not this label."""

    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String(30)), default=list, server_default="{}")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    subjects: Mapped[list[Subject]] = relationship(secondary=stream_subjects, order_by=Subject.name)


# ---------- Accounts ----------

class User(Timestamped, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(_in("role", ROLES), name="role"),
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True)   # used only for recovery; never shown to others
    username: Mapped[str] = mapped_column(String(20), unique=True)  # what the student logs in with
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="student", server_default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"))
    stream_id: Mapped[int | None] = mapped_column(ForeignKey("streams.id", ondelete="SET NULL"))
    # My Path: chosen career, finished steps with dates and notes, and skills. Deleted with the account.
    saved_progress: Mapped[dict | None] = mapped_column(JSONB)
    saved_progress_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    path_changes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")   # changes of the sign-up career

    @property
    def path(self) -> str:
        """The career chosen at sign-up. It stays fixed for the account."""
        return (self.saved_progress or {}).get("path", "")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=lambda: datetime.now(UTC)
    )

    region: Mapped[Region | None] = relationship()
    stream: Mapped[Stream | None] = relationship()


class UserSession(Timestamped, Base):
    """A logged-in device. Only a hash of the token is stored, so a database leak can't log anyone in."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped[User] = relationship()


class RateLimitEvent(Timestamped, Base):
    __tablename__ = "rate_limit_events"
    __table_args__ = (Index("ix_rate_limit_events_key_created_at", "key", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64))


# ---------- Trust ----------

class Source(Timestamped, Base):
    """Where a piece of information came from, so a student can check it themselves."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500), unique=True)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class VerificationRecord(Timestamped, Base):
    """One status change on any record: what changed, who did it and why."""

    __tablename__ = "verification_records"
    __table_args__ = (
        CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),
        Index("ix_verification_records_entity", "entity_type", "entity_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(25))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"))
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    note: Mapped[str | None] = mapped_column(Text)


class UpdateHistory(Timestamped, Base):
    """A permanent log of changes to data."""

    __tablename__ = "update_history"
    __table_args__ = (Index("ix_update_history_entity", "entity_type", "entity_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50))
    changes: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class Trusted:
    """Every record students rely on says where it came from, for which year, and how far it has been checked."""

    academic_year: Mapped[str | None] = mapped_column(String(9))
    last_updated: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(25), default="pending_verification", server_default="pending_verification", index=True)

    @declared_attr
    def source_id(cls) -> Mapped[int | None]:
        return mapped_column(ForeignKey("sources.id", ondelete="SET NULL"))

    @declared_attr
    def source(cls) -> Mapped[Source | None]:
        return relationship(Source)

    @declared_attr.directive
    def __table_args__(cls):
        return (CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),)


# ---------- Fields, courses and exams ----------

class Field(Trusted, Base):
    """A broad area such as Law or Aviation, explained for someone who has never heard of it."""

    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    tagline: Mapped[str] = mapped_column(String(200))
    what_is_it: Mapped[str] = mapped_column(Text)
    what_you_learn: Mapped[str] = mapped_column(Text)
    who_can_choose: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[str] = mapped_column(Text)
    further_education: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    courses: Mapped[list["Course"]] = relationship(back_populates="field", order_by="Course.name")


course_exams = Table(
    "course_exams",
    Base.metadata,
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("exam_id", ForeignKey("entrance_exams.id", ondelete="CASCADE"), primary_key=True),
)
course_careers = Table(
    "course_careers",
    Base.metadata,
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("career_id", ForeignKey("career_paths.id", ondelete="CASCADE"), primary_key=True),
)


class CareerPath(Base):
    __tablename__ = "career_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))


class EntranceExam(Trusted, Base):
    __tablename__ = "entrance_exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    conducted_by: Mapped[str] = mapped_column(String(150))
    summary: Mapped[str] = mapped_column(Text)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), index=True)

    region: Mapped[Region | None] = relationship()


class Course(Trusted, Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="RESTRICT"), index=True)
    kind: Mapped[str] = mapped_column(String(40))   # e.g. "Degree", "Professional qualification"
    summary: Mapped[str] = mapped_column(Text)
    what_you_study: Mapped[str] = mapped_column(Text)
    duration: Mapped[str] = mapped_column(String(150))
    admission: Mapped[str] = mapped_column(Text)
    path_note: Mapped[str] = mapped_column(Text, default="", server_default="")
    path_years: Mapped[int | None] = mapped_column(Integer)

    field: Mapped[Field] = relationship(back_populates="courses")
    exams: Mapped[list[EntranceExam]] = relationship(secondary=course_exams, order_by=EntranceExam.name)
    careers: Mapped[list[CareerPath]] = relationship(secondary=course_careers, order_by=CareerPath.name)
    criteria: Mapped[list["EligibilityCriterion"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="EligibilityCriterion.id"
    )


eligibility_regions = Table(
    "eligibility_regions",
    Base.metadata,
    Column("criterion_id", ForeignKey("eligibility_criteria.id", ondelete="CASCADE"), primary_key=True),
    Column("region_id", ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True),
)
eligibility_group_subjects = Table(
    "eligibility_group_subjects",
    Base.metadata,
    Column("group_id", ForeignKey("eligibility_groups.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
)


class EligibilityCriterion(Trusted, Base):
    """
    One route into a course. A course with two routes (such as NDA's Army and Air Force wings)
    has two rows. With no regions it applies across India; with regions it applies only there.
    """

    __tablename__ = "eligibility_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(120))
    summary: Mapped[str] = mapped_column(Text)
    subjects_known: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    min_percentage: Mapped[float | None] = mapped_column(Numeric(4, 1))
    min_percentage_reserved: Mapped[float | None] = mapped_column(Numeric(4, 1))
    min_age: Mapped[int | None] = mapped_column(Integer)
    max_age: Mapped[int | None] = mapped_column(Integer)

    course: Mapped[Course] = relationship(back_populates="criteria")
    regions: Mapped[list[Region]] = relationship(secondary=eligibility_regions)
    groups: Mapped[list["EligibilityGroup"]] = relationship(
        back_populates="criterion", cascade="all, delete-orphan", order_by="EligibilityGroup.id"
    )


class EligibilityGroup(Base):
    """
    'At least min_count of these subjects'. Every group of a rule must be met, so
    Physics AND Maths AND (Chemistry OR Biology) is three groups, and 3-of-4 is one.
    """

    __tablename__ = "eligibility_groups"
    __table_args__ = (CheckConstraint("min_count >= 1", name="min_count"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    criterion_id: Mapped[int] = mapped_column(ForeignKey("eligibility_criteria.id", ondelete="CASCADE"), index=True)
    min_count: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    criterion: Mapped[EligibilityCriterion] = relationship(back_populates="groups")
    subjects: Mapped[list[Subject]] = relationship(secondary=eligibility_group_subjects, order_by=Subject.name)


# ---------- Colleges ----------

FACT_KINDS = ("fees", "placements", "facilities", "admission")


class ImportBatch(Timestamped, Base):
    """One official file. Its rows wait in staging until a person approves the whole batch."""

    __tablename__ = "import_batches"
    __table_args__ = (CheckConstraint(_in("status", ("pending", "published", "rejected")), name="status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_sha256: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(10), default="pending", server_default="pending", index=True)
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_new: Mapped[int] = mapped_column(Integer, default=0)
    rows_changed: Mapped[int] = mapped_column(Integer, default=0)
    rows_unchanged: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    rows_missing: Mapped[int] = mapped_column(Integer, default=0)
    problems: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")   # first few rejected rows
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source: Mapped[Source] = relationship()


class CollegeStaging(Base):
    """A collected row. Students can never see this table."""

    __tablename__ = "college_staging"
    __table_args__ = (
        CheckConstraint(_in("action", ("new", "changed", "unchanged")), name="action"),
        Index("ix_college_staging_batch_id_aishe_code", "batch_id", "aishe_code", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id", ondelete="CASCADE"))
    aishe_code: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(10))
    data: Mapped[dict] = mapped_column(JSONB)


class College(Trusted, Base):
    """A real institution from an official directory. Nothing here is typed in by hand or generated."""

    __tablename__ = "colleges"

    id: Mapped[int] = mapped_column(primary_key=True)
    aishe_code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(300), index=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id", ondelete="RESTRICT"), index=True)
    district: Mapped[str | None] = mapped_column(String(100), index=True)
    year_established: Mapped[int | None] = mapped_column(Integer)
    location: Mapped[str | None] = mapped_column(String(50))
    college_type: Mapped[str | None] = mapped_column(String(100), index=True)
    management: Mapped[str | None] = mapped_column(String(100), index=True)
    university_name: Mapped[str | None] = mapped_column(String(300))
    university_type: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(300))
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.id", ondelete="SET NULL"))

    region: Mapped[Region] = relationship()
    offerings: Mapped[list["CollegeCourse"]] = relationship(back_populates="college", cascade="all, delete-orphan", order_by="CollegeCourse.id")
    facts: Mapped[list["CollegeFact"]] = relationship(back_populates="college", cascade="all, delete-orphan", order_by="CollegeFact.kind")


class Branch(Base):
    """A specialisation inside a course, when one course has several."""

    __tablename__ = "branches"
    __table_args__ = (Index("ix_branches_course_id_name", "course_id", "name", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(150))


class CollegeCourse(Trusted, Base):
    """A course a college offers. Added only by an admin, with the source they read it from."""

    __tablename__ = "college_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id", ondelete="SET NULL"))

    college: Mapped[College] = relationship(back_populates="offerings")
    course: Mapped[Course] = relationship()
    branch: Mapped[Branch | None] = relationship()


class CollegeFact(Trusted, Base):
    """Fees, placements, facilities or admission details. Never stored without a source and an academic year."""

    __tablename__ = "college_facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(15))
    value: Mapped[str] = mapped_column(Text)

    college: Mapped[College] = relationship(back_populates="facts")

    @declared_attr.directive
    def __table_args__(cls):
        return (
            CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),
            CheckConstraint(_in("kind", FACT_KINDS), name="kind"),
        )


# ---------- Languages ----------

class Translation(Base):
    """Text in another language for any record. A new language needs rows here, not new columns."""

    __tablename__ = "translations"
    __table_args__ = (Index("ix_translations_lookup", "entity_type", "entity_id", "field", "language", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(30))
    entity_id: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(40))
    language: Mapped[str] = mapped_column(String(5))
    text: Mapped[str] = mapped_column(Text)


# ---------- Roadmaps ----------

roadmap_courses = Table(
    "roadmap_courses",
    Base.metadata,
    Column("roadmap_id", ForeignKey("roadmaps.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


class Roadmap(Trusted, Base):
    """A year-by-year plan towards one career. Advice to follow, not an admission rule."""

    __tablename__ = "roadmaps"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    uses_semesters: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    courses: Mapped[list[Course]] = relationship(secondary=roadmap_courses, order_by=Course.name)
    steps: Mapped[list["RoadmapStep"]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan",
        order_by="(RoadmapStep.year, RoadmapStep.semester, RoadmapStep.position)",
    )


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"
    __table_args__ = (
        Index("ix_roadmap_steps_place", "roadmap_id", "year", "semester", "position", unique=True),
        CheckConstraint("year BETWEEN 1 AND 6", name="year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    semester: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    why: Mapped[str] = mapped_column(Text)
    build_task: Mapped[str] = mapped_column(Text)
    resources: Mapped[str] = mapped_column(Text, default="", server_default="")

    roadmap: Mapped[Roadmap] = relationship(back_populates="steps")


class UserStepProgress(Timestamped, Base):
    __tablename__ = "user_step_progress"
    __table_args__ = (Index("ix_user_step_progress_user_step", "user_id", "step_id", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    step_id: Mapped[int] = mapped_column(ForeignKey("roadmap_steps.id", ondelete="CASCADE"))


# ---------- Quiz ----------

quiz_option_courses = Table(
    "quiz_option_courses",
    Base.metadata,
    Column("option_id", ForeignKey("quiz_options.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, unique=True)
    text: Mapped[str] = mapped_column(String(300))
    weight: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    options: Mapped[list["QuizOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QuizOption.id"
    )


class QuizOption(Base):
    __tablename__ = "quiz_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("quiz_questions.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(300))

    question: Mapped[QuizQuestion] = relationship(back_populates="options")
    courses: Mapped[list[Course]] = relationship(secondary=quiz_option_courses)


class QuizResult(Timestamped, Base):
    """A saved result. `results` is a snapshot, so later quiz edits never change it."""

    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    answered: Mapped[int] = mapped_column(Integer, default=0)
    results: Mapped[list] = mapped_column(JSONB, default=list)
    also: Mapped[list] = mapped_column(JSONB, default=list)


# ---------- Exam dates ----------

important_date_courses = Table(
    "important_date_courses",
    Base.metadata,
    Column("date_id", ForeignKey("important_dates.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)
CERTAINTIES = ("CONFIRMED", "REPORTED", "NOT_ANNOUNCED")


class ImportantDate(Trusted, Base):
    """A real exam or deadline. Past dates vanish by themselves, and `certainty` says how sure we are."""

    __tablename__ = "important_dates"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True)
    certainty: Mapped[str] = mapped_column(String(15))
    starts_on: Mapped[date | None] = mapped_column(Date, index=True)
    ends_on: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str] = mapped_column(Text, default="", server_default="")
    checked_on: Mapped[date] = mapped_column(Date)

    courses: Mapped[list[Course]] = relationship(secondary=important_date_courses)

    @declared_attr.directive
    def __table_args__(cls):
        return (
            CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),
            CheckConstraint(_in("certainty", CERTAINTIES), name="certainty"),
        )


class Scholarship(Trusted, Base):
    """A scholarship, loan or official portal. If the rules could not be read, the text says so."""

    __tablename__ = "scholarships"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    run_by: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(15))
    audience: Mapped[str] = mapped_column(String(15))
    state: Mapped[str | None] = mapped_column(String(5))
    who_can_apply: Mapped[str] = mapped_column(Text)
    what_you_get: Mapped[str] = mapped_column(Text)
    how_to_apply: Mapped[str] = mapped_column(Text)
    apply_url: Mapped[str] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    @declared_attr.directive
    def __table_args__(cls):
        return (CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),)


tech_change_roadmaps = Table(
    "tech_change_roadmaps",
    Base.metadata,
    Column("tech_change_id", ForeignKey("tech_changes.id", ondelete="CASCADE"), primary_key=True),
    Column("roadmap_id", ForeignKey("roadmaps.id", ondelete="CASCADE"), primary_key=True),
)


class TechChange(Trusted, Base):
    """A real change in technology, with its evidence and the careers it affects."""

    __tablename__ = "tech_changes"
    __table_args__ = (CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    level: Mapped[str] = mapped_column(String(15))
    what_changed: Mapped[str] = mapped_column(Text)
    why_it_matters: Mapped[str] = mapped_column(Text)
    learn_next: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    roadmaps: Mapped[list[Roadmap]] = relationship(secondary=tech_change_roadmaps)


class CareerOpportunity(Trusted, Base):
    """One next step after finishing a roadmap. It links to real listings and never invents vacancies."""

    __tablename__ = "career_opportunities"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "kind"),
        CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(15))
    title: Mapped[str] = mapped_column(String(120))
    detail: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    roadmap: Mapped[Roadmap] = relationship()


class CourseListing(Trusted, Base):
    """One line in the full course list. Detail is optional, so a course can be listed before it has a page."""

    __tablename__ = "course_listings"
    __table_args__ = (
        UniqueConstraint("name", "state"),
        CheckConstraint(_in("status", VERIFICATION_STATUSES), name="status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    group_name: Mapped[str] = mapped_column(String(60))
    duration: Mapped[str] = mapped_column(String(60), default="", server_default="")
    state: Mapped[str] = mapped_column(String(10))
    route: Mapped[str] = mapped_column(String(60))
    course_slug: Mapped[str | None] = mapped_column(String(60))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class SourceWatch(Base):
    """An official page we check for changes. It alerts an admin and never changes student content."""

    __tablename__ = "source_watches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(String(500), unique=True)
    affects: Mapped[str] = mapped_column(String(200))
    content_hash: Mapped[str | None] = mapped_column(String(64))
    last_text: Mapped[str | None] = mapped_column(Text)
    change_summary: Mapped[str | None] = mapped_column(Text)
    last_error: Mapped[str | None] = mapped_column(String(200))
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")


class Precheck(Base):
    """A record Claude compared with its official source. The fingerprint is its text at that moment, so an edit clears the mark."""

    __tablename__ = "prechecks"
    __table_args__ = (UniqueConstraint("entity_type", "entity_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(20))
    entity_id: Mapped[int] = mapped_column(Integer)
    fingerprint: Mapped[str] = mapped_column(String(64))
    checked_on: Mapped[date] = mapped_column(Date)


# ---------- Reports, updates and job sources ----------

class Report(Timestamped, Base):
    """A visitor saying something on a page is wrong. This is how content stays true."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    page: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)


class TechnologyUpdate(Timestamped, Base):
    """A headline or useful tool. Only the title, link and date are kept: students read it on the original site."""

    __tablename__ = "technology_updates"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    link: Mapped[str] = mapped_column(String(500), unique=True)
    source_name: Mapped[str] = mapped_column(String(100))
    why_it_matters: Mapped[str] = mapped_column(Text, default="", server_default="")
    is_tool: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    careers: Mapped[list[str]] = mapped_column(ARRAY(String(40)), default=list, server_default="{}")


class OpportunitySource(Base):
    """A trusted place to find real openings. We link to them and never copy or invent vacancies."""

    __tablename__ = "opportunity_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    url: Mapped[str] = mapped_column(String(300), unique=True)
    description: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


# ---------- Skills ----------

skill_roadmaps = Table(
    "skill_roadmaps",
    Base.metadata,
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("roadmap_id", ForeignKey("roadmaps.id", ondelete="CASCADE"), primary_key=True),
)


class Skill(Trusted, Base):
    """Something worth learning. With no roadmaps it helps in every career."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    category: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(150))
    why: Mapped[str] = mapped_column(Text)
    project: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    roadmaps: Mapped[list[Roadmap]] = relationship(secondary=skill_roadmaps)
    resources: Mapped[list["LearningResource"]] = relationship(cascade="all, delete-orphan", order_by="LearningResource.id")


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(300))


class UserSkill(Timestamped, Base):
    """One line of a student's personal checklist."""

    __tablename__ = "user_skills"
    __table_args__ = (
        Index("ix_user_skills_user_skill", "user_id", "skill_id", unique=True),
        CheckConstraint(_in("state", ("learning", "done")), name="state"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    state: Mapped[str] = mapped_column(String(10))


class PathChangeRequest(Timestamped, Base):
    """A student's request to change their career after their one free change. An admin answers it."""

    __tablename__ = "path_change_requests"
    __table_args__ = (
        Index("ix_path_change_requests_user", "user_id"),
        CheckConstraint(_in("status", ("pending", "approved", "rejected")), name="status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    from_path: Mapped[str] = mapped_column(String(80))
    to_path: Mapped[str] = mapped_column(String(80))
    reason: Mapped[str] = mapped_column(String(300), default="", server_default="")
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    user: Mapped[User] = relationship(foreign_keys=[user_id])


class PasswordReset(Timestamped, Base):
    """A one-time reset code. Only its hash is kept. It expires, and allows only a few tries."""

    __tablename__ = "password_resets"
    __table_args__ = (Index("ix_password_resets_user", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
