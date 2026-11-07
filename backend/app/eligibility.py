"""
Compares a student's Class 12 subjects with a course's rules.

The wording never promises admission. A match means "your subjects fit the rule we have",
and marks, age, exams and seats still decide the outcome.
"""
from app.models import Course, EligibilityCriterion
from app.schemas import EligibilityResult


def _applies(criterion: EligibilityCriterion, region_id: int | None) -> bool:
    region_ids = {region.id for region in criterion.regions}
    return not region_ids or region_id in region_ids


def group_text(group) -> str:
    names = [subject.name for subject in group.subjects]
    if len(names) == 1:
        return names[0]
    if group.min_count == 1:
        return "one of " + ", ".join(names)
    return f"{group.min_count} of " + ", ".join(names)


def _missing(criterion: EligibilityCriterion, subject_ids: set[int]) -> list[str]:
    missing = []
    for group in criterion.groups:
        have = sum(1 for subject in group.subjects if subject.id in subject_ids)
        if have < group.min_count:
            missing.append(group_text(group))
    return missing


def check(
    course: Course, subject_ids: set[int] | None, region_id: int | None, visible: tuple[str, ...]
) -> EligibilityResult:
    """`subject_ids` is None when the student hasn't told us their subjects."""
    criteria = [c for c in course.criteria if c.status in visible and _applies(c, region_id)]
    if not criteria:
        return EligibilityResult(
            status="no_rule",
            message="We don't have a confirmed rule for this yet. Ask the college or check the official site.",
        )

    known = [criterion for criterion in criteria if criterion.subjects_known]
    if not known:
        return EligibilityResult(status="check", message="The subject rule needs checking on the official site.")

    if all(not criterion.groups for criterion in known):
        return EligibilityResult(
            status="eligible",
            message="The rule we have doesn't ask for specific Class 12 subjects. Marks, age and exams may still apply.",
        )
    if subject_ids is None:
        return EligibilityResult(status="need_subjects", message="Tell us your subjects to check this.")

    best: list[str] | None = None
    for criterion in known:
        missing = _missing(criterion, subject_ids)
        if not missing:
            return EligibilityResult(
                status="eligible",
                message="Your subjects fit the rule we have. Marks, age and exams may still apply.",
            )
        if best is None or len(missing) < len(best):
            best = missing
    return EligibilityResult(
        status="not_eligible",
        message="Your subjects don't fit the rule we have.",
        missing=best or [],
    )
