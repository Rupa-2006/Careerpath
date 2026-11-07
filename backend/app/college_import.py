"""
Reads the official college directory into staging. Nothing here touches what students see:
a person reviews the batch, and only then does publish_batch apply it.
"""
import hashlib
import re
from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy import func, insert, select, update
from sqlalchemy.orm import Session

from app.models import College, CollegeStaging, ImportBatch, Region, Source

SOURCE_NAME = "All Colleges as per AISHE Dashboard (Ministry of Education, on AIKosh)"
SOURCE_URL = "https://aikosh.indiaai.gov.in/home/datasets/details/all_colleges_as_per_aishe_dashboard_3.html"
MAX_ROWS = 200_000
MAX_PROBLEMS_KEPT = 50
MAX_MISSING_SHARE = 0.10   # a file losing more than this looks broken, so it needs an explicit override

# Our column -> headers we accept, compared without spaces or punctuation
COLUMNS = {
    "aishe_code": {"aishecode", "aishecodeid"},
    "name": {"nameoftheinstitution", "nameofinstitution", "institutionname", "collegename", "name"},
    "state": {"state", "statename"},
    "district": {"district", "districtname"},
    "year_established": {"yearofestablishment", "yearestablished"},
    "location": {"location"},
    "college_type": {"collegetype", "typeofcollege"},
    "management": {"management", "managementtype"},
    "university_name": {"affiliateduniversityname", "universityname"},
    "university_type": {"affiliateduniversitytype", "universitytype"},
}
REQUIRED = ("aishe_code", "name", "state")
FIELDS = tuple(column for column in COLUMNS if column != "state") + ("region_id",)

# Older or shortened names official files may use
STATE_ALIASES = {
    "orissa": "Odisha", "pondicherry": "Puducherry", "uttaranchal": "Uttarakhand", "chattisgarh": "Chhattisgarh",
    "nctofdelhi": "Delhi", "andamanandnicobar": "Andaman and Nicobar Islands",
    "dadraandnagarhaveli": "Dadra and Nagar Haveli and Daman and Diu",
    "damananddiu": "Dadra and Nagar Haveli and Daman and Diu",
}


class ImportRefused(Exception):
    """The whole file is unsafe to use, and the message says why."""


def _key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower().replace("&", "and"))


def _text(value: object, limit: int) -> str | None:
    cleaned = " ".join(str(value).split()) if value is not None else ""
    return cleaned[:limit] or None


def read_rows(path: Path) -> Iterator[dict]:
    """Finds the header row, then yields each row as {our column: value}."""
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        for sheet in workbook.worksheets:
            rows = sheet.iter_rows(values_only=True)
            for _, header in zip(range(15), rows):
                positions = {}
                for index, cell in enumerate(header):
                    for column, names in COLUMNS.items():
                        if _key(cell) in names and column not in positions:
                            positions[column] = index
                if all(column in positions for column in REQUIRED):
                    for values in rows:
                        if any(value not in (None, "") for value in values):
                            yield {column: values[index] if index < len(values) else None for column, index in positions.items()}
                    return
    finally:
        workbook.close()
    raise ImportRefused("This file doesn't have the expected columns: AISHE Code, Name and State.")


def _clean(raw: dict, regions: dict[str, int], this_year: int) -> tuple[dict | None, str | None]:
    code = _text(raw.get("aishe_code"), 20)
    name = _text(raw.get("name"), 300)
    if not code or not name:
        return None, "Missing AISHE code or name"
    state_key = _key(raw.get("state"))
    region_id = regions.get(state_key) or regions.get(_key(STATE_ALIASES.get(state_key)))
    if region_id is None:
        return None, f"{code}: unknown State '{_text(raw.get('state'), 60)}'"
    year = None
    if raw.get("year_established") not in (None, ""):
        match = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", str(raw["year_established"]))
        if match and int(match.group()) <= this_year:
            year = int(match.group())
    return {
        "aishe_code": code,
        "name": name,
        "region_id": region_id,
        "district": _text(raw.get("district"), 100),
        "year_established": year,
        "location": _text(raw.get("location"), 50),
        "college_type": _text(raw.get("college_type"), 100),
        "management": _text(raw.get("management"), 100),
        "university_name": _text(raw.get("university_name"), 300),
        "university_type": _text(raw.get("university_type"), 100),
    }, None


def stage_file(db: Session, path: Path) -> ImportBatch:
    """Reads a file into a pending batch and works out what would change. Publishes nothing."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if db.scalar(select(ImportBatch).where(ImportBatch.status == "pending")):
        raise ImportRefused("Another import is waiting for review. Publish or reject it first.")
    # A rejected file, or an older list that became right again, may come back. Only a repeat of the live one is pointless.
    latest = db.scalar(
        select(ImportBatch.file_sha256).where(ImportBatch.status == "published").order_by(ImportBatch.id.desc()).limit(1)
    )
    if latest == digest:
        raise ImportRefused("This exact file is already published.")

    regions = {_key(name): region_id for region_id, name in db.execute(select(Region.id, Region.name))}
    current = {college.aishe_code: college for college in db.scalars(select(College))}
    this_year = date.today().year

    seen: dict[str, dict] = {}
    problems: list[str] = []
    rejected = read = 0
    for raw in read_rows(path):
        read += 1
        if read > MAX_ROWS:
            raise ImportRefused(f"This file has more than {MAX_ROWS} rows, which is not expected.")
        row, problem = _clean(raw, regions, this_year)
        if row and row["aishe_code"] in seen:
            row, problem = None, f"{row['aishe_code']}: appears twice in the file"
        if row is None:
            rejected += 1
            if len(problems) < MAX_PROBLEMS_KEPT:
                problems.append(problem)
            continue
        seen[row["aishe_code"]] = row
    if not seen:
        raise ImportRefused("No usable rows were found in this file.")

    staged, counts = [], {"new": 0, "changed": 0, "unchanged": 0}
    for code, row in seen.items():
        college = current.get(code)
        if college is None:
            action = "new"
        else:
            action = "changed" if any(getattr(college, field) != row[field] for field in FIELDS) else "unchanged"
        counts[action] += 1
        staged.append({"aishe_code": code, "action": action, "data": row})

    source = db.scalar(select(Source).where(Source.url == SOURCE_URL))
    if source is None:
        source = Source(name=SOURCE_NAME, url=SOURCE_URL, is_official=True)
        db.add(source)
        db.flush()
    batch = ImportBatch(
        source_id=source.id, file_name=path.name[:255], file_sha256=digest, rows_read=read,
        rows_new=counts["new"], rows_changed=counts["changed"], rows_unchanged=counts["unchanged"],
        rows_rejected=rejected, rows_missing=sum(1 for code, college in current.items() if code not in seen and college.status == "published"),
        problems=problems,
    )
    db.add(batch)
    db.flush()
    db.execute(insert(CollegeStaging), [{**item, "batch_id": batch.id} for item in staged])
    db.commit()
    return batch


def publish_batch(db: Session, batch: ImportBatch, reviewer_id, allow_large_removal: bool = False) -> None:
    """Applies an approved batch. Colleges missing from the file are marked outdated, never deleted."""
    if batch.status != "pending":
        raise ImportRefused("This import has already been reviewed.")
    live = db.scalar(select(func.count()).select_from(College).where(College.status == "published"))
    if batch.rows_missing > MAX_MISSING_SHARE * live and not allow_large_removal:
        raise ImportRefused(
            f"{batch.rows_missing} colleges are missing from this file, which is unusually many. "
            "Check that the file is complete before publishing."
        )

    today = date.today()
    trust = {"status": "published", "source_id": batch.source_id, "last_updated": today, "batch_id": batch.id}
    staged = db.scalars(select(CollegeStaging).where(CollegeStaging.batch_id == batch.id, CollegeStaging.action != "unchanged"))
    current = {college.aishe_code: college for college in db.scalars(select(College))}
    fresh = []
    for item in staged:
        college = current.get(item.aishe_code)
        if college is None:
            fresh.append({**item.data, **trust})
        else:
            for field, value in {**item.data, **trust}.items():
                setattr(college, field, value)
    if fresh:
        db.execute(insert(College), fresh)

    in_file = select(CollegeStaging.aishe_code).where(CollegeStaging.batch_id == batch.id)
    db.execute(
        update(College).where(College.aishe_code.not_in(in_file), College.status == "published").values(status="outdated")
    )
    db.execute(
        update(College).where(College.aishe_code.in_(in_file), College.status == "outdated").values(status="published")
    )
    batch.status, batch.reviewed_by, batch.reviewed_at = "published", reviewer_id, datetime.now(UTC)
    db.query(CollegeStaging).filter(CollegeStaging.batch_id == batch.id).delete()
    db.commit()


def reject_batch(db: Session, batch: ImportBatch, reviewer_id) -> None:
    if batch.status != "pending":
        raise ImportRefused("This import has already been reviewed.")
    batch.status, batch.reviewed_by, batch.reviewed_at = "rejected", reviewer_id, datetime.now(UTC)
    db.query(CollegeStaging).filter(CollegeStaging.batch_id == batch.id).delete()
    db.commit()
