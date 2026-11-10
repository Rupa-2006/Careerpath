"""
Loads roadmaps, the quiz, exam dates, job sources and Telugu text:  python -m scripts.seed_journey
Run seed_reference and seed_content first. Safe to run again: review status and student progress are kept,
because steps are matched by their place in the roadmap and are never deleted.
"""
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models import (
    Course,
    ImportantDate,
    OpportunitySource,
    QuizOption,
    QuizQuestion,
    Roadmap,
    RoadmapStep,
    Source,
    TechnologyUpdate,
    Translation,
)
from scripts.content import ACADEMIC_YEAR, CHECKED, SOURCES
from scripts.stepora.courses import COURSES as STEPORA_COURSES
from scripts.stepora.dates import DATES
from scripts.stepora.quiz import QUIZ
from scripts.stepora.roadmaps import GOALS
from scripts.stepora.roadmaps_more import MORE_GOALS
from scripts.stepora.roadmaps_path import PATH_GOALS
from scripts.stepora.roadmaps_path2 import MORE_PATH_GOALS
from scripts.stepora.roadmaps_extra import CHEMICAL, LAB, MINING, PERFORMER, TEACHER, link_courses, with_extra_steps

with_extra_steps(MORE_GOALS + PATH_GOALS + MORE_PATH_GOALS)
for _new_goal in (CHEMICAL, MINING, TEACHER, LAB, PERFORMER):
    if _new_goal not in MORE_PATH_GOALS:
        MORE_PATH_GOALS.append(_new_goal)
link_courses(GOALS + MORE_GOALS + PATH_GOALS + MORE_PATH_GOALS)

ROADMAP_SOURCES = {
    "web-developer": "aicte", "cyber-security-analyst": "cert-in", "data-analyst": "data-gov",
    "embedded-engineer": "nptel", "pharmacist": "pci", "accounts-finance": "icai", "civil-services": "upsc",
    "doctor": "nmc", "nurse": "inc", "agriculture-officer": "icar", "mechanical-engineer": "nptel", "advocate": "bci",
    "civil-engineer": "nptel", "electrical-engineer": "nptel", "dentist": "knruhs", "physiotherapist": "knruhs",
    "designer": "nid", "hotel-manager": "nchm", "ai-engineer": "nist-ai-rmf", "business-manager": "ugc", "architect": "nata", "researcher": "iiser", "pilot": "igrua",
    "defence-officer": "upsc-nda", "government-exams": "ssc", "vocational-professional": "ugc-bvoc",
    "company-secretary": "icsi", "health-technologist": "knruhs", "physical-education-teacher": "tg-pecet",
    "animal-and-fisheries": "eapcet-ap", "traditional-medicine-doctor": "neet-2026", "social-worker": "dost",
    "chemical-engineer": "nptel", "mining-metallurgy-engineer": "nptel", "teacher": "ugc", "lab-analyst": "nptel", "performing-artist": "ugc",
}
TOOLS = [
    ("NotebookLM: an AI study assistant for your own notes", "https://notebooklm.google/", "Google",
     "Upload your lecture notes or PDFs and ask questions about them. Useful for revision, but always check answers against your textbook.",
     "మీ లెక్చర్ నోట్స్ లేదా PDFలు అప్‌లోడ్ చేసి వాటి గురించి ప్రశ్నలు అడగవచ్చు. రివిజన్‌కు ఉపయోగం, కానీ జవాబులను మీ పాఠ్యపుస్తకంతో తప్పకుండా సరిచూసుకోండి."),
    ("GitHub Student Developer Pack", "https://education.github.com/pack", "GitHub",
     "Free developer tools and services for verified students. Useful for building and deploying your projects.",
     "ధృవీకరించబడిన విద్యార్థులకు ఉచిత డెవలపర్ టూల్స్, సేవలు. మీ ప్రాజెక్ట్‌లు నిర్మించడానికి, ఆన్‌లైన్‌లో పెట్టడానికి ఉపయోగం."),
]
JOB_SOURCES = [
    ("National Career Service (NCS)", "https://www.ncs.gov.in/",
     "Government of India portal for jobs, career counselling, internships and job fairs.",
     "ఉద్యోగాలు, కెరీర్ కౌన్సెలింగ్, ఇంటర్న్‌షిప్‌లు, జాబ్ ఫెయిర్ల కోసం భారత ప్రభుత్వ పోర్టల్."),
    ("Internshala", "https://internshala.com/",
     "Popular website for student internships, including work-from-home options.",
     "విద్యార్థుల ఇంటర్న్‌షిప్‌ల కోసం ప్రసిద్ధ వెబ్‌సైట్, వర్క్-ఫ్రమ్-హోమ్ అవకాశాలతో సహా."),
    ("Skill India Digital Hub", "https://www.skillindiadigital.gov.in/",
     "Government platform for skill courses, certifications and apprenticeship opportunities.",
     "నైపుణ్య కోర్సులు, సర్టిఫికేషన్లు, అప్రెంటిస్‌షిప్ అవకాశాల కోసం ప్రభుత్వ వేదిక."),
    ("Apprenticeship India", "https://www.apprenticeshipindia.gov.in/",
     "Government portal for paid apprenticeships with companies across India.",
     "భారతదేశమంతటా కంపెనీల్లో స్టైపెండ్ ఉన్న అప్రెంటిస్‌షిప్‌ల కోసం ప్రభుత్వ పోర్టల్."),
]


class Telugu:
    """Collects translations, replacing old text for the same field."""

    def __init__(self, db):
        self.db = db

    def put(self, entity_type: str, entity_id: int, **fields) -> None:
        for field, text in fields.items():
            self.db.execute(delete(Translation).where(
                Translation.entity_type == entity_type, Translation.entity_id == entity_id,
                Translation.field == field, Translation.language == "te",
            ))
            if text:
                self.db.add(Translation(entity_type=entity_type, entity_id=entity_id, field=field, language="te", text=text))


def source_for(db, key: str) -> Source:
    name, url = SOURCES[key]
    source = db.scalar(select(Source).where(Source.url == url))
    if source is None:
        source = Source(name=name, url=url, is_official=True)
        db.add(source)
        db.flush()
    return source


def load_roadmaps(db, telugu, courses) -> int:
    count = 0
    for order, data in enumerate(GOALS + MORE_GOALS + PATH_GOALS + MORE_PATH_GOALS, start=1):
        roadmap = db.scalar(select(Roadmap).where(Roadmap.slug == data["slug"]))
        if roadmap is None:
            roadmap = Roadmap(slug=data["slug"])
            db.add(roadmap)
        roadmap.name, roadmap.description = data["name_en"], data["description_en"]
        roadmap.uses_semesters = data.get("uses_semesters", True)
        roadmap.sort_order, roadmap.academic_year, roadmap.last_updated = order, ACADEMIC_YEAR, CHECKED
        roadmap.source = source_for(db, ROADMAP_SOURCES[data["slug"]])
        roadmap.courses = [courses[slug] for slug in data["courses"]]
        db.flush()
        telugu.put("roadmap", roadmap.id, name=data["name_te"], description=data["description_te"])

        for year, semester, position, title, title_te, why, why_te, resources, build, build_te in data["steps"]:
            place = {"roadmap_id": roadmap.id, "year": year, "semester": semester, "position": position}
            step = db.scalar(select(RoadmapStep).filter_by(**place))
            if step is None:
                step = RoadmapStep(**place)
                db.add(step)
            step.title, step.why, step.build_task, step.resources = title, why, build, resources
            db.flush()
            telugu.put("step", step.id, title=title_te, why=why_te, build_task=build_te)
            count += 1
    return count


def load_quiz(db, telugu, courses) -> None:
    """Saved results are snapshots, so replacing the questions can't change them."""
    for old in db.scalars(select(QuizOption.id)).all():
        telugu.put("quiz_option", old, text=None)
    for old in db.scalars(select(QuizQuestion.id)).all():
        telugu.put("quiz_question", old, text=None)
    db.execute(delete(QuizQuestion))
    for position, (text, text_te, weight, options) in enumerate(QUIZ, start=1):
        question = QuizQuestion(position=position, text=text, weight=weight)
        db.add(question)
        db.flush()
        telugu.put("quiz_question", question.id, text=text_te)
        for option_text, option_te, slugs in options:
            option = QuizOption(question=question, text=option_text, courses=[courses[slug] for slug in slugs])
            db.add(option)
            db.flush()
            telugu.put("quiz_option", option.id, text=option_te)


def load_dates(db, telugu, courses) -> None:
    for data in DATES:
        item = db.scalar(select(ImportantDate).where(ImportantDate.title == data["title_en"]))
        if item is None:
            item = ImportantDate(title=data["title_en"], checked_on=data["checked_on"], certainty=data["status"])
            db.add(item)
        item.certainty, item.starts_on, item.ends_on = data["status"], data.get("starts_on"), data.get("ends_on")
        item.note, item.checked_on = data.get("note_en", ""), data["checked_on"]
        item.academic_year, item.last_updated = ACADEMIC_YEAR, data["checked_on"]
        url = data["source_url"]
        source = db.scalar(select(Source).where(Source.url == url))
        if source is None:
            source = Source(name=url.split("/")[2].removeprefix("www."), url=url, is_official=True)
            db.add(source)
        item.source = source
        item.courses = [courses[slug] for slug in data["courses"]]
        db.flush()
        telugu.put("date", item.id, title=data.get("title_te"), note=data.get("note_te"))


def load_links(db, telugu) -> None:
    for title, link, source, why, why_te in TOOLS:
        item = db.scalar(select(TechnologyUpdate).where(TechnologyUpdate.link == link))
        if item is None:
            item = TechnologyUpdate(link=link, is_tool=True)
            db.add(item)
        item.title, item.source_name, item.why_it_matters = title, source, why
        db.flush()
        telugu.put("update", item.id, why_it_matters=why_te)
    for order, (name, url, description, description_te) in enumerate(JOB_SOURCES, start=1):
        item = db.scalar(select(OpportunitySource).where(OpportunitySource.url == url))
        if item is None:
            item = OpportunitySource(url=url)
            db.add(item)
        item.name, item.description, item.sort_order = name, description, order
        db.flush()
        telugu.put("opportunity_source", item.id, description=description_te)


def main() -> None:
    with SessionLocal() as db:
        courses = {course.slug: course for course in db.scalars(select(Course))}
        telugu = Telugu(db)
        for data in STEPORA_COURSES:
            telugu.put("course", courses[data["slug"]].id, summary=data["summary_te"], what_you_study=data.get("what_you_study_te"))
        steps = load_roadmaps(db, telugu, courses)
        load_quiz(db, telugu, courses)
        load_dates(db, telugu, courses)
        load_links(db, telugu)
        db.commit()
    print(f"Journey ready: {len(GOALS + MORE_GOALS + PATH_GOALS + MORE_PATH_GOALS)} roadmaps, {steps} steps, {len(QUIZ)} quiz questions, {len(DATES)} dates.")


if __name__ == "__main__":
    main()
