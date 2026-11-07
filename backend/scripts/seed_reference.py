"""
Loads reference data:  python -m scripts.seed_reference
Safe to run again. These are India's 28 States and 8 Union Territories and common Class 12 subject groups.
Eligibility will later use subjects, because streams differ between boards.
"""
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Region, Stream, Subject

STATES = {
    "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh", "AS": "Assam", "BR": "Bihar", "CG": "Chhattisgarh",
    "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
    "KA": "Karnataka", "KL": "Kerala", "MP": "Madhya Pradesh", "MH": "Maharashtra", "MN": "Manipur",
    "ML": "Meghalaya", "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha", "PB": "Punjab",
    "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu", "TS": "Telangana", "TR": "Tripura",
    "UP": "Uttar Pradesh", "UK": "Uttarakhand", "WB": "West Bengal",
}
UNION_TERRITORIES = {
    "AN": "Andaman and Nicobar Islands", "CH": "Chandigarh",
    "DN": "Dadra and Nagar Haveli and Daman and Diu", "DL": "Delhi", "JK": "Jammu and Kashmir",
    "LA": "Ladakh", "LD": "Lakshadweep", "PY": "Puducherry",
}
SUBJECTS = {
    "physics": "Physics", "chemistry": "Chemistry", "mathematics": "Mathematics", "biology": "Biology",
    "accountancy": "Accountancy", "business-studies": "Business Studies / Commerce", "economics": "Economics",
    "history": "History", "political-science": "Political Science / Civics", "english": "English",
    "biotechnology": "Biotechnology", "computer-science": "Computer Science / IT",
    "engineering-graphics": "Engineering Graphics", "technical-vocational": "Technical Vocational Subject",
}
# (slug, name, local names, subjects)
STREAMS = [
    ("science-maths", "Science with Maths", ["PCM", "MPC"], ["physics", "chemistry", "mathematics"]),
    ("science-biology", "Science with Biology", ["PCB", "BiPC"], ["physics", "chemistry", "biology"]),
    ("science-both", "Science with Maths and Biology", ["PCMB"], ["physics", "chemistry", "mathematics", "biology"]),
    ("commerce-maths", "Commerce with Maths", ["MEC"], ["mathematics", "economics", "accountancy", "business-studies"]),
    ("commerce", "Commerce", ["CEC"], ["economics", "accountancy", "business-studies", "political-science"]),
    ("arts", "Arts / Humanities", ["HEC"], ["history", "economics", "political-science"]),
    ("vocational", "Vocational", [], []),
    ("other", "Other or not sure", [], []),
]


def main() -> None:
    with SessionLocal() as db:
        for kind, group in (("state", STATES), ("union_territory", UNION_TERRITORIES)):
            for code, name in group.items():
                if db.scalar(select(Region).where(Region.code == code)) is None:
                    db.add(Region(code=code, name=name, kind=kind))

        subjects = {}
        for slug, name in SUBJECTS.items():
            subjects[slug] = db.scalar(select(Subject).where(Subject.slug == slug)) or Subject(slug=slug, name=name)
            db.add(subjects[slug])

        for order, (slug, name, aliases, subject_slugs) in enumerate(STREAMS, start=1):
            stream = db.scalar(select(Stream).where(Stream.slug == slug))
            if stream is None:
                stream = Stream(slug=slug, name=name, aliases=aliases, sort_order=order)
                db.add(stream)
            # English is studied in nearly every board; "vocational" and "other" stay empty, so we ask instead
            stream.subjects = [subjects[item] for item in subject_slugs] + ([subjects["english"]] if subject_slugs else [])
        db.commit()
    print(f"Reference data ready: {len(STATES)} States, {len(UNION_TERRITORIES)} Union Territories, {len(STREAMS)} streams")


if __name__ == "__main__":
    main()
