"""
Keeps official data up to date by itself, safely.

- DOST course list: new course names are added and published automatically, because they are copied
  word for word from the official list. Removed names are never deleted: an admin is alerted to check.
- Exam dates: when an official page starts mentioning the next year, an admin is alerted with the
  exact sentence, so a person sets the date. Dates are never guessed from page text.
"""
import html
import re
from collections.abc import Callable
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CourseListing, ImportantDate, Source, SourceWatch
from app.watch import fetch, page_text

DOST_URL = "https://dost.cgg.gov.in/viewUGCourses.htm"
# A real list has well over a hundred courses. Far fewer means the page changed or broke, so nothing is touched.
MIN_COURSES = 100
GROUPS = (("B.A", "Arts"), ("B.Sc", "Science"), ("B.Com", "Commerce"), ("BBA", "Management"), ("BBM", "Management"),
          ("BCA", "Computer Applications"), ("BSW", "Social Work"), ("B.Vocational", "Vocational"), ("Diploma", "Diploma"),
          ("M.", "Integrated (5 years)"))


def dost_courses(raw: str) -> dict[str, str]:
    """Course name to length in years, read from the DOST course table."""
    found: dict[str, str] = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I):
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cell))).strip() for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)]
        if len(cells) >= 3 and "-->" in cells[1]:
            name = re.sub(r"\s+", " ", cells[1].split("-->", 1)[1]).strip()
            found.setdefault(name, cells[2])
    return found


def group_of(name: str) -> str:
    return next((group for prefix, group in GROUPS if name.startswith(prefix)), "Other")


def alert(db: Session, key: str, name: str, affects: str, summary: str) -> None:
    watch = db.scalar(select(SourceWatch).where(SourceWatch.url == key))
    if watch is None:
        watch = SourceWatch(url=key, name=name, affects=affects)
        db.add(watch)
    if watch.change_summary != summary or not watch.needs_review:
        watch.change_summary, watch.needs_review = summary[:600], True
        watch.last_changed_at = datetime.now(UTC)
    watch.last_checked_at = datetime.now(UTC)


def sync_dost(db: Session, read: Callable[[str], str] = fetch) -> str:
    try:
        courses = dost_courses(read(DOST_URL))
    except Exception as problem:  # noqa: BLE001 - a broken site must not stop the daily update
        return f"DOST: could not read ({str(problem)[:80]})"
    if len(courses) < MIN_COURSES:
        alert(db, f"{DOST_URL}#sync", "DOST course list", "Full course list for Telangana",
              f"Only {len(courses)} courses were found, so nothing was changed. The page may have changed its layout.")
        db.commit()
        return f"DOST: only {len(courses)} found, nothing changed"
    source = db.scalar(select(Source).where(Source.url == DOST_URL))
    rows = {row.name: row for row in db.scalars(select(CourseListing).where(CourseListing.state == "TS", CourseListing.route == "DOST"))}
    added = []
    for name, years in courses.items():
        if name not in rows:
            db.add(CourseListing(
                name=name, group_name=group_of(name), duration=f"{years.replace(',', ' or ')} years", state="TS", route="DOST",
                status="published", source=source, academic_year=None, last_updated=date.today(),
            ))
            added.append(name)
    gone = sorted(name for name, row in rows.items() if name not in courses and row.status != "outdated")
    if gone:
        alert(db, f"{DOST_URL}#removed", "DOST course list", "Full course list for Telangana",
              "No longer on the official list, so please check and mark them out of date: " + "; ".join(gone))
    db.commit()
    return f"DOST: {len(courses)} on the list, {len(added)} added, {len(gone)} to check"


NEXT_YEAR_WORDS = re.compile(r"notification|schedule|exam date|examination|apply|application|time ?table", re.I)


def check_dates(db: Session, read: Callable[[str], str] = fetch) -> str:
    """Alerts an admin when the official page for a not-yet-announced date starts mentioning that year."""
    flagged = 0
    for item in db.scalars(select(ImportantDate).where(ImportantDate.certainty == "NOT_ANNOUNCED", ImportantDate.status == "published")):
        year = re.search(r"20\d\d", item.title)
        if not (year and item.source):
            continue
        try:
            text = page_text(read(item.source.url))
        except Exception:  # noqa: BLE001 - one broken site must not stop the others
            continue
        lines = [line for line in text.split("\n") if year[0] in line and NEXT_YEAR_WORDS.search(line) and f"{int(year[0]) - 1}-{year[0][2:]}" not in line and f"{int(year[0]) - 1}-{year[0]}" not in line]
        if lines:
            alert(db, f"{item.source.url}#date-{item.id}", f"Date: {item.title}", "Exam dates",
                  "The official page now mentions this year. Please read it and set the date: " + " / ".join(lines[:3]))
            flagged += 1
    db.commit()
    return f"Dates: {flagged} may now be announced"
