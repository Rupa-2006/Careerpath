"""
Loads the starter catalogue:  python -m scripts.seed_content
Run seed_reference first. Safe to run again: existing records and their review status are left alone.
Use --overwrite to replace text from scripts/content.py. It still keeps each record's review status.
"""
import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import (
    CareerPath,
    Course,
    EligibilityCriterion,
    EligibilityGroup,
    EntranceExam,
    Field,
    Region,
    Source,
    Subject,
)
from scripts.course_paths import COURSE_PATHS
from scripts.content import ACADEMIC_YEAR, CHECKED, COURSES, EXAMS, EXAMS_CHECKED_LATER, FIELDS, LATER_CHECK, SOURCES

TRUST = {"academic_year": ACADEMIC_YEAR, "last_updated": CHECKED}


def get_or_new(db, model, **lookup):
    row = db.scalar(select(model).filter_by(**lookup))
    if row is not None:
        return row, False
    row = model(**lookup)
    db.add(row)
    return row, True


def load_sources(db) -> dict[str, Source]:
    sources = {}
    for key, (name, url) in SOURCES.items():
        sources[key], _ = get_or_new(db, Source, url=url)
        sources[key].name = name
        sources[key].is_official = True
    db.flush()
    return sources


def load_fields(db, sources, overwrite) -> dict[str, Field]:
    fields = {}
    columns = ("name", "tagline", "what_is_it", "what_you_learn", "who_can_choose", "required_skills", "further_education")
    for order, (slug, *text, source) in enumerate(FIELDS, start=1):
        field, created = get_or_new(db, Field, slug=slug)
        if created or overwrite:
            for column, value in zip(columns, text):
                setattr(field, column, value)
            field.sort_order, field.source = order, sources[source]
            for name, value in TRUST.items():
                setattr(field, name, value)
        fields[slug] = field
    db.flush()
    return fields


def load_exams(db, sources, overwrite) -> dict[str, EntranceExam]:
    regions = {region.code: region for region in db.scalars(select(Region))}
    exams = {}
    for slug, name, conducted_by, summary, source, region in EXAMS:
        exam, created = get_or_new(db, EntranceExam, slug=slug)
        if created or overwrite:
            exam.name, exam.conducted_by, exam.summary = name, conducted_by, summary
            exam.source, exam.region = sources[source], regions.get(region)
            for key, value in TRUST.items():
                setattr(exam, key, value)
            if slug in EXAMS_CHECKED_LATER:
                exam.last_updated = LATER_CHECK
        exams[slug] = exam
    db.flush()
    return exams


def load_criteria(db, course, rules, sources):
    """A rule keeps its row, and so its review status, when only its text changes."""
    regions = {region.code: region for region in db.scalars(select(Region))}
    subjects = {subject.slug: subject for subject in db.scalars(select(Subject))}
    existing = {criterion.label: criterion for criterion in course.criteria}
    for rule in rules:
        criterion = existing.pop(rule["label"], None)
        if criterion is None:
            criterion = EligibilityCriterion(label=rule["label"], summary=rule["summary"], **TRUST)
            course.criteria.append(criterion)
        criterion.summary = rule["summary"]
        criterion.source = sources[rule["source"]]
        criterion.subjects_known = rule.get("known", True)
        for name in ("min_percentage", "min_percentage_reserved", "min_age", "max_age"):
            setattr(criterion, name, rule.get(name))
        criterion.regions = [regions[code] for code in rule.get("regions", [])]
        criterion.groups = [
            EligibilityGroup(min_count=count, subjects=[subjects[slug] for slug in names])
            for count, names in rule["groups"]
        ]
    for leftover in existing.values():
        course.criteria.remove(leftover)


def load_courses(db, fields, exams, sources, overwrite) -> None:
    for data in COURSES:
        course, created = get_or_new(db, Course, slug=data["slug"])
        course.path_years, course.path_note = COURSE_PATHS.get(data["slug"], (None, ""))
        if not (created or overwrite):
            continue
        course.name, course.kind, course.summary = data["name"], data["kind"], data["summary"]
        course.what_you_study, course.duration, course.admission = data["study"], data["duration"], data["admission"]
        course.field, course.source = fields[data["field"]], sources[data["source"]]
        for key, value in TRUST.items():
            setattr(course, key, value)
        course.last_updated = data.get("checked", CHECKED)
        course.exams = [exams[slug] for slug in data["exams"]]
        careers = []
        for name in data["careers"]:
            career, _ = get_or_new(db, CareerPath, slug=name.lower().replace(" ", "-"))
            career.name = name
            careers.append(career)
        course.careers = careers
        db.flush()
        load_criteria(db, course, data["criteria"], sources)


def main(overwrite: bool = False) -> None:
    with SessionLocal() as db:
        sources = load_sources(db)
        fields = load_fields(db, sources, overwrite)
        exams = load_exams(db, sources, overwrite)
        load_courses(db, fields, exams, sources, overwrite)
        db.commit()
    print(f"Catalogue ready: {len(FIELDS)} fields, {len(COURSES)} courses, {len(EXAMS)} exams. New records await review.")


if __name__ == "__main__":
    main(overwrite="--overwrite" in sys.argv)
