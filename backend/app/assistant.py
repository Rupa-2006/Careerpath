"""
The Career Assistant's answers. Everything here comes from CareerPath's own records and eligibility
rules, so it works with no AI account, and it can't invent a course, a rule or a date.

It presents options and reasons. It never picks for the student and never promises a result.
"""
import re
from dataclasses import dataclass, field as dataclass_field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.catalog import COURSE_LOAD, visible
from app.eligibility import check
from app.models import Course, EntranceExam, Field, ImportantDate, Roadmap, Skill
from app.schemas import AssistantCard, EligibilityResult

MAX_OPTIONS = 6
CHECK_OFFICIAL = "Please confirm the rules on the official website before you apply."

# What a student might say, and the fields it points to. A link to explore, not a judgement of the student.
INTERESTS: dict[str, tuple[str, ...]] = {
    "coding": ("engineering", "computer", "science"), "programming": ("engineering", "computer", "science"), "computer": ("engineering", "computer", "science"),
    "software": ("engineering", "computer", "science"), "app": ("engineering", "computer", "science"), "ai": ("engineering", "computer", "science"),
    "cyber": ("engineering", "computer", "science"), "cs": ("engineering", "computer", "science"), "technology": ("engineering", "computer", "science"),
    "machine": ("engineering", "diploma"), "electronic": ("engineering", "diploma"), "robot": ("engineering",),
    "btech": ("engineering",), "math": ("engineering", "science", "commerce"),
    "physics": ("engineering", "science"), "chemistry": ("science", "pharmacy"), "research": ("science",),
    "biology": ("medical", "pharmacy", "agriculture"), "doctor": ("medical",), "hospital": ("medical", "pharmacy"),
    "health": ("medical", "pharmacy"), "nurse": ("medical",), "medicine": ("medical", "pharmacy"), "patient": ("medical",),
    "farming": ("agriculture",), "plant": ("agriculture",), "food": ("agriculture", "hospitality"),
    "money": ("commerce", "management"), "business": ("commerce", "management"), "account": ("commerce",),
    "finance": ("commerce", "management"), "bank": ("commerce", "government"), "startup": ("management",),
    "lawyer": ("law",), "justice": ("law",), "court": ("law",), "drawing": ("design", "arts"), "art": ("design", "arts"),
    "creative": ("design", "arts"), "fashion": ("design",), "history": ("arts",), "writing": ("arts",),
    "language": ("arts",), "people": ("arts", "management", "hospitality"), "helping": ("medical", "law", "arts"), "travel": ("hospitality", "aviation"),
    "hotel": ("hospitality",), "cooking": ("hospitality",), "tourism": ("hospitality",), "flying": ("aviation",),
    "pilot": ("aviation",), "aircraft": ("aviation",), "army": ("defence",), "navy": ("defence",), "uniform": ("defence",),
    "ias": ("government",), "practical": ("diploma", "vocational", "skills"), "trade": ("vocational", "diploma"),
    "polytechnic": ("diploma",),
}
# Everyday short names. "cs" is left out of the course names because students mean Computer Science by it
COURSE_WORDS = {"cse": "btech-cse", "ece": "btech-ece", "mechanical": "btech-mech", "nursing": "bsc-nursing", "pharmacy": "bpharm"}
AMBIGUOUS = {"cs"}
# Students say these without naming a state. "eamcet" is the exam's old name, still widely used
EXAM_WORDS = {"eapcet": ("ap-eapcet", "tg-eapcet"), "eamcet": ("ap-eapcet", "tg-eapcet"), "lawcet": ("ap-lawcet", "tg-lawcet"), "pecet": ("ap-pecet", "tg-pecet"), "ecet": ("ap-ecet", "tg-ecet")}

# How students name a career in their own words
CAREER_WORDS = {
    "hacker": ("cyber-security-analyst",), "hacking": ("cyber-security-analyst",), "ethical hacker": ("cyber-security-analyst",),
    "cyber security": ("cyber-security-analyst",), "cybersecurity": ("cyber-security-analyst",),
    "data scientist": ("data-analyst", "ai-engineer"), "data science": ("data-analyst", "ai-engineer"),
    "ai": ("ai-engineer",), "artificial intelligence": ("ai-engineer",), "machine learning": ("ai-engineer",),
    "software engineer": ("web-developer",), "software developer": ("web-developer",), "programmer": ("web-developer",),
    "app developer": ("web-developer",), "web developer": ("web-developer",),
    "lawyer": ("advocate",), "ias": ("civil-services",), "ips": ("civil-services",), "collector": ("civil-services",),
    "army": ("defence-officer",), "navy": ("defence-officer",), "air force": ("defence-officer",),
    "chartered accountant": ("accounts-finance",), "businessman": ("business-manager",), "manager": ("business-manager",),
    "game designer": ("designer",), "animator": ("designer",), "vet": ("animal-and-fisheries",),
}
# Words that turn the next phrase into something the student does not want
NOT_WANTED = ("not ", "no ", "don t want", "dont want", "don t like", "dont like", "hate ", "bad at ", "failed in ", "fail in ", "weak in ", "not good at ")
# Words that show the student's own interest, as opposed to what others want
OWN_LIKE = ("i like ", "i love ", "i enjoy ", "interested in ", "my interest")


def unwanted(spaced: str, phrase: str) -> bool:
    """True when the phrase comes right after "not", "hate", "failed in" and similar words."""
    at = spaced.find(f" {phrase} ")
    return at >= 0 and any(marker in spaced[max(0, at - 14):at + 1] for marker in NOT_WANTED)


CRISIS = (
    "kill myself", "killing myself", "suicide", "suicidal", "end my life", "want to die", "wanna die", "self harm",
    "hurt myself", "no reason to live", "better off dead", "ఆత్మహత్య", "చనిపోవాలి",
)
GREETINGS = {"hi", "hello", "hey", "namaste", "namaskaram", "thanks", "thank", "you", "ok", "okay"}
WORRIES = {"scared", "afraid", "worried", "worry", "stress", "stressed", "anxious", "pressure", "failed", "failing", "fail", "tension"}
WORRY_TEXT = (
    "It's normal to feel unsure about this, and one result doesn't decide your whole future. Most students have more paths "
    "than they can see right now. If the worry feels heavy, talk to someone you trust, or call Tele-MANAS free on 14416."
)
PROMISE_WORDS = ("guarantee", "guaranteed", "surely", "definitely", "100", "sure job", "will i get", "can i get a job")
MISSING_FACTS = {
    "salary": ("salary", "package", "lpa", "earn", "income", "pay"),
    "scholarship": ("scholarship", "scholarships", "education loan", "fee reimbursement"),
    "fees": ("fee", "fees", "cost"),
    "cutoffs": ("cutoff", "cut off", "rank", "marks needed", "seat"),
    "colleges": ("college", "university", "campus", "placement"),
}
MISSING_TEXT = {
    "salary": "I don't have checked salary figures, and pay varies a lot by employer, city and experience, so I won't guess.",
    "scholarship": "The Scholarships page lists central schemes, loans and state portals with official links. Please confirm the rules there before you apply.",
    "fees": "I don't have checked fee amounts here. The college's official page has the current figures.",
    "cutoffs": "I don't have checked cutoffs, ranks or seat numbers. They change every year, so use the official counselling site.",
    "colleges": "I can't rank colleges or predict placements. Check the official NIRF rankings and your state counselling website.",
}


@dataclass
class Student:
    subject_ids: set[int] | None
    region_id: int | None


@dataclass
class Reply:
    intent: str
    text: str
    cards: list[AssistantCard] = dataclass_field(default_factory=list)
    next_questions: list[str] = dataclass_field(default_factory=list)


def clean(text: str) -> str:
    """Lower case, words only, and "B.Tech" and "btech" treated as the same thing."""
    text = re.sub(r"[^a-z0-9ఀ-౿]+", " ", text.lower()).strip()
    return re.sub(r"\b([bm]) (tech|sc|com|arch|des|pharm|voc|ed|ba)\b", r"\1\2", text)


def names_of(name: str, slug: str = "") -> set[str]:
    """The ways a student could write a record's name: "BCA (Bachelor of ...)" gives both parts."""
    if name.startswith("B.Tech CSE ("):
        return {clean(name)}   # "B.Tech CSE" alone means the main branch, not every specialisation
    found = {clean(name), clean(slug)}
    bracketed = re.fullmatch(r"(.+?) \((.+)\)", name)   # not "B.Sc (Hons) Agriculture", which would match every B.Sc
    if bracketed:
        found |= {clean(bracketed[1]), clean(bracketed[2])}
    return {item for item in found if len(item) >= 2 and item not in AMBIGUOUS}


def says(spaced: str, phrase: str) -> bool:
    return f" {phrase} " in spaced


def mentioned(spaced: str, records: list, slug: bool = True) -> list:
    return [item for item in records if any(says(spaced, phrase) for phrase in names_of(item.name, item.slug if slug else ""))]


def field_names(field: Field) -> set[str]:
    return names_of(field.name) | {clean(field.name.split(" and ")[0])}


def trust(record) -> dict:
    return {
        "status": record.status, "academic_year": record.academic_year,
        "last_updated": record.last_updated, "source": record.source,
    }


def course_card(course: Course, why: str, result: EligibilityResult) -> AssistantCard:
    return AssistantCard(
        **trust(course), kind="course", title=course.name, to=f"/courses/{course.slug}", why=why,
        detail=f"{course.summary} {course.kind}, {course.duration}.", eligibility=result,
    )


def load_courses(db: Session) -> list[Course]:
    return db.scalars(
        select(Course).options(*COURSE_LOAD, selectinload(Course.careers), selectinload(Course.exams))
        .where(Course.status.in_(visible())).order_by(Course.name)
    ).unique().all()


def join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def spread(courses: list[Course]) -> list[Course]:
    """Takes turns between fields, so one field can't fill the whole list."""
    by_field: dict[int, list[Course]] = {}
    for course in courses:
        by_field.setdefault(course.field_id, []).append(course)
    ordered = []
    while any(by_field.values()):
        for group in by_field.values():
            if group:
                ordered.append(group.pop(0))
    return ordered


def options(courses: list[Course], student: Student, why, opening: str, weight=lambda course: 0) -> Reply:
    """Shows only paths the rules leave open, says what was left out, and never ranks a winner."""
    shown = visible()
    results = {course.id: check(course, student.subject_ids, student.region_id, shown) for course in courses}
    open_paths = [course for course in courses if results[course.id].status != "not_eligible"]
    closed = [course for course in courses if results[course.id].status == "not_eligible"]
    fits_first = sorted(open_paths, key=lambda course: (-weight(course), results[course.id].status != "eligible"))
    chosen = spread(fits_first)[:MAX_OPTIONS]
    cards = [course_card(course, why(course), results[course.id]) for course in chosen]

    if not chosen:
        text = f"{opening} None of the paths I have there fit the subjects you chose."
    else:
        text = f"{opening} Here are {len(chosen)} paths to compare. They aren't in order of which is best, because that depends on you."
    if len(chosen) == 1:
        text = f"{opening} I only have 1 path that fits here, so please look at other fields too."
    if closed:
        names = [course.name for course in closed[:3]] + (["others"] if len(closed) > 3 else [])
        text += f" I left out {join(names)}"
        text += ", because the rule I have asks for subjects you didn't choose."
    if student.subject_ids is None:
        text += " Add your Class 12 subjects above, so I can check which of these fit you."
    text += f" {CHECK_OFFICIAL}"

    follow = [f"Compare {chosen[0].name.split(' (')[0]} and {chosen[1].name.split(' (')[0]}"] if len(chosen) >= 2 else []
    if chosen:
        follow.append(f"Tell me about {chosen[0].name.split(' (')[0]}")
    return Reply("options", text, cards, follow)


def for_student(exam: EntranceExam, student: Student) -> bool:
    """A state exam is left out only when we know the student lives in a different state."""
    return exam.region_id is None or student.region_id is None or exam.region_id == student.region_id


def explain_course(db: Session, course: Course, student: Student) -> Reply:
    result = check(course, student.subject_ids, student.region_id, visible())
    exams = [exam.name for exam in course.exams if exam.status in visible() and for_student(exam, student)]
    careers = [career.name for career in course.careers]
    text = f"{course.name}: {course.summary} {result.message}"
    if result.missing:
        text += f" You would need: {'; '.join(result.missing)}."
    if exams:
        text += f" Entrance exams linked to it: {join(exams)}."
    if careers:
        text += f" It can lead to work such as {join(careers[:4])}, though no course promises a job."
    text += f" {CHECK_OFFICIAL}"
    cards = [course_card(course, "This is the course you asked about.", result)]

    others = [
        item for item in load_courses(db)
        if item.field_id == course.field_id and item.id != course.id
        and check(item, student.subject_ids, student.region_id, visible()).status != "not_eligible"
    ]
    for item in others[:2]:
        cards.append(course_card(
            item, f"Another path in {course.field.name}, so you can compare before you decide.",
            check(item, student.subject_ids, student.region_id, visible()),
        ))
    follow = [f"What skills do I need for {course.name.split(' (')[0]}?"]
    if others:
        follow.insert(0, f"Compare {course.name.split(' (')[0]} and {others[0].name.split(' (')[0]}")
    return Reply("course", text, cards, follow)


def compare_courses(chosen: list[Course], student: Student) -> Reply:
    chosen = chosen[:3]
    cards = []
    for course in chosen:
        exams = [exam.name for exam in course.exams if exam.status in visible()]
        why = f"Field: {course.field.name}. Entrance: {join(exams) if exams else 'no exam linked here'}."
        cards.append(course_card(course, why, check(course, student.subject_ids, student.region_id, visible())))
    text = (
        f"Here is how {join([course.name.split(' (')[0] for course in chosen])} differ. "
        "I won't pick one for you: look at what you would study each day, the exams, and how long each takes. "
        f"{CHECK_OFFICIAL}"
    )
    reply = Reply("compare", text, cards)
    reply.next_questions = [f"Tell me about {course.name.split(' (')[0]}" for course in chosen[:2]]
    return reply


def explain_exam(db: Session, exam: EntranceExam, student: Student) -> Reply:
    linked = [course for course in load_courses(db) if any(item.id == exam.id for item in course.exams)]
    text = f"{exam.name}, run by {exam.conducted_by}: {exam.summary} {CHECK_OFFICIAL}"
    cards = [AssistantCard(**trust(exam), kind="exam", title=exam.name, to=None, why="This is the exam you asked about.", detail=exam.summary)]
    shown = visible()
    cards += [
        course_card(course, f"{exam.name} is linked to this course.", check(course, student.subject_ids, student.region_id, shown))
        for course in linked[:3]
    ]
    return Reply("exam", text, cards, [f"When is {exam.name}?"])


def explain_field(db: Session, field: Field, student: Student) -> Reply:
    text = f"{field.name}: {field.what_is_it} {field.who_can_choose} Skills that help: {field.required_skills}"
    card = AssistantCard(**trust(field), kind="field", title=field.name, to=f"/explore/{field.slug}", why="This is the field you asked about.", detail=field.tagline)
    courses = [course for course in load_courses(db) if course.field_id == field.id]
    found = options(courses, student, lambda course: f"This is a path in {field.name}.", "")
    found.text = f"{text} {found.text.strip()}"
    found.intent = "field"
    found.cards.insert(0, card)
    return found


def compare_fields(fields: list[Field]) -> Reply:
    cards = [
        AssistantCard(**trust(item), kind="field", title=item.name, to=f"/explore/{item.slug}", why=item.who_can_choose, detail=f"{item.what_is_it} Skills that help: {item.required_skills}")
        for item in fields
    ]
    text = (
        f"{join([item.name for item in fields])} are very different, and neither is better for everyone, so I won't pick one for you. "
        "Compare what you would do each day, which subjects each needs, and which skills you enjoy using."
    )
    return Reply("compare", text, cards, [f"What is {item.name.split(' and ')[0].lower()}?" for item in fields[:2]])


def roadmap_reply(roadmaps: list[Roadmap]) -> Reply:
    cards = [
        AssistantCard(**trust(item), kind="roadmap", title=item.name, to=f"/roadmaps/{item.slug}", why="A year-by-year plan you can follow and tick off.", detail=item.description)
        for item in roadmaps[:3]
    ]
    text = f"I have a year-by-year plan for {join([item.name for item in roadmaps[:3]])}. It's advice to follow, not an admission rule, and it doesn't promise a job."
    return Reply("roadmap", text, cards, [f"What skills do I need for {roadmaps[0].name}?"])


def skills_reply(db: Session, roadmaps: list[Roadmap]) -> Reply:
    query = select(Skill).options(joinedload(Skill.source), selectinload(Skill.roadmaps)).where(Skill.status.in_(visible())).order_by(Skill.sort_order)
    found = db.scalars(query).unique().all()
    ids = {item.id for item in roadmaps}
    own = [item for item in found if ids & {road.id for road in item.roadmaps}]
    general = [item for item in found if not item.roadmaps]
    picked = (own[:4] + general[:2]) if ids else general[:MAX_OPTIONS]
    if not picked:
        return Reply("no_data", "I don't have any reviewed skills to suggest yet.")
    cards = [
        AssistantCard(**trust(item), kind="skill", title=item.name, to="/skills", why=item.why, detail=f"Try this: {item.project}")
        for item in picked
    ]
    subject = f"for {join([item.name for item in roadmaps[:2]])}" if roadmaps else "that help in most careers"
    return Reply("skills", f"Here are skills {subject}. Each has a small project, so you can show what you learned.", cards)


def dates_reply(db: Session, courses: list[Course], exams: list[EntranceExam]) -> Reply:
    query = select(ImportantDate).options(joinedload(ImportantDate.source), selectinload(ImportantDate.courses)).where(ImportantDate.status.in_(visible()))
    found = db.scalars(query.order_by(ImportantDate.starts_on.asc().nulls_last())).unique().all()
    today = date.today()
    ahead = [item for item in found if (item.ends_on or item.starts_on or today) >= today]
    linked = {course.id for course in courses} | {
        course.id for course in load_courses(db) if {exam.id for exam in course.exams} & {exam.id for exam in exams}
    }
    if linked:
        ahead = [item for item in ahead if linked & {course.id for course in item.courses}]
    # A course can have several dates, so a named exam's own dates come before anything else linked to it
    ahead = [item for item in ahead if any(exam.name.lower() in item.title.lower() for exam in exams)] or ahead
    if not ahead:
        return Reply("no_data", f"I don't have a reviewed date for that yet, so I won't guess. The official website is the place to check.", [], [])
    cards = [
        AssistantCard(
            **trust(item), kind="date", title=item.title, to="/dates", why=f"How sure this is: {item.certainty}.",
            detail=f"{item.starts_on.isoformat() if item.starts_on else 'Date not announced yet'}. {item.note}".strip(),
        )
        for item in ahead[:MAX_OPTIONS]
    ]
    return Reply("dates", f"Here are the dates I have. Dates can change, so check the official site before you rely on one.", cards)


def crisis_reply(lang: str) -> Reply:
    text = (
        "I'm really sorry you're feeling this way, and you don't have to carry it alone. "
        "Please talk to someone now: call Tele-MANAS on 14416 or 1-800-891-4416. It's the Government of India's free mental health "
        "helpline. If you're in immediate danger, call 112. It can also help to tell a parent, teacher or friend you trust. "
        "One exam or one result does not decide your whole life, and your career questions can wait until you're ready."
    )
    if lang == "te":
        text += " మీరు ఒంటరి కాదు. దయచేసి ఇప్పుడే 14416కు కాల్ చేయండి."
    return Reply("crisis", text)


def answer(db: Session, message: str, student: Student, lang: str = "en") -> Reply:
    text = clean(message)
    spaced = f" {text} "
    words = set(text.split())
    if any(phrase in spaced or phrase in message.lower() for phrase in CRISIS):
        return crisis_reply(lang)
    if words and words <= GREETINGS:
        return Reply(
            "welcome",
            "Hello! Tell me what you enjoy, or ask about a course, an exam or a career. I'll show options and explain why, and you decide.",
            [], ["What can I do after Class 12?", "I like coding", "What is law?"],
        )

    courses = load_courses(db)
    if not courses:
        return Reply("no_data", "Our team hasn't finished reviewing the course records yet, so I have nothing checked to tell you. Please try again later.")

    exams = db.scalars(select(EntranceExam).options(joinedload(EntranceExam.source)).where(EntranceExam.status.in_(visible()))).all()
    fields = db.scalars(select(Field).options(joinedload(Field.source)).where(Field.status.in_(visible())).order_by(Field.sort_order)).all()
    roadmaps = db.scalars(select(Roadmap).options(joinedload(Roadmap.source)).where(Roadmap.status.in_(visible())).order_by(Roadmap.sort_order)).all()

    named = mentioned(spaced, courses)
    for word, slug in COURSE_WORDS.items():
        extra = next((course for course in courses if course.slug == slug), None)
        if word in words and extra and extra not in named:
            named.append(extra)
    refused = {slug for word, slug in COURSE_WORDS.items() if unwanted(spaced, word)}
    named = [course for course in named if course.slug not in refused and not any(unwanted(spaced, phrase) for phrase in names_of(course.name, course.slug))]
    courses = [course for course in courses if course.slug not in refused]
    named_exams = mentioned(spaced, exams)
    for word, slugs in EXAM_WORDS.items():
        if word in words and not named_exams:
            named_exams = [exam for exam in exams if exam.slug in slugs and for_student(exam, student)]
    named_roads = mentioned(spaced, roadmaps)
    for phrase, slugs in CAREER_WORDS.items():
        if says(spaced, phrase) and not unwanted(spaced, phrase):
            named_roads += [road for road in roadmaps if road.slug in slugs and road not in named_roads]
    named_roads = [road for road in named_roads if not any(unwanted(spaced, phrase) for phrase in names_of(road.name, road.slug))]
    named_fields = [item for item in fields if any(says(spaced, phrase) for phrase in field_names(item))]
    career_courses = [course for course in courses if any(says(spaced, clean(career.name)) and not unwanted(spaced, clean(career.name)) for career in course.careers)]

    gaps = [MISSING_TEXT[topic] for topic, hints in MISSING_FACTS.items() if any(says(spaced, hint) for hint in hints)]
    promise = any(word in spaced for word in PROMISE_WORDS)

    reply = route(db, spaced, words, student, courses, fields, named, named_exams, named_roads, named_fields, career_courses)
    lead = []
    if promise:
        lead.append("Nobody can promise a seat or a job, and I won't either. Results depend on marks, exams, seats, skills and the job market.")
    if words & WORRIES:
        lead.append(WORRY_TEXT)
    lead += gaps
    if lead:
        if reply.intent == "unknown":
            reply = Reply("limits", "", [], ["What can I do after Class 12?"])
        reply.text = " ".join(lead + ([reply.text] if reply.text else []))
    return reply


def route(db, spaced, words, student, courses, fields, named, named_exams, named_roads, named_fields, career_courses) -> Reply:
    if words & {"when", "date", "dates", "deadline", "schedule"} or says(spaced, "last date"):
        return dates_reply(db, named, named_exams)
    if words & {"skill", "skills", "learn"}:
        linked = named_roads or [road for road in db.scalars(select(Roadmap).options(selectinload(Roadmap.courses)).where(Roadmap.status.in_(visible()))).all() if {item.id for item in road.courses} & {item.id for item in named}]
        return skills_reply(db, linked)
    if len(named) >= 2:
        return compare_courses(named, student)
    if named_roads and (words & {"roadmap", "plan", "become", "steps", "career", "job", "jobs"} or not named):
        return roadmap_reply(named_roads)
    if named_exams and not named:
        return explain_exam(db, named_exams[0], student)
    if named:
        return explain_course(db, named[0], student)
    if career_courses and not named_fields:
        names = join([course.name for course in career_courses[:3]])
        return options(career_courses, student, lambda course: "This course can lead to the work you mentioned.", f"These paths can lead there: {names}.")
    own = any(marker in spaced for marker in OWN_LIKE)
    interest_first = own and any(word in words or f"{word}s" in words for word in INTERESTS)
    if len(named_fields) >= 2 and not interest_first:
        return compare_fields(named_fields[:3])
    if named_fields and not interest_first:
        return explain_field(db, named_fields[0], student)

    every = [word for word in INTERESTS if word in words or f"{word}s" in words]
    disliked = [word for word in every if unwanted(spaced, word) or unwanted(spaced, f"{word}s")]
    liked = [word for word in every if word not in disliked]
    avoid = {slug for word in disliked for slug in INTERESTS[word]} - {slug for word in liked for slug in INTERESTS[word]}
    not_careers = {phrase for phrase in {clean(career.name) for course in courses for career in course.careers} if unwanted(spaced, phrase)}
    courses = [course for course in courses if not {clean(career.name) for career in course.careers} & not_careers]
    if liked:
        reasons: dict[str, list[str]] = {}
        for word in liked:
            for slug in INTERESTS[word]:
                reasons.setdefault(slug, []).append(word)
        return options(
            [course for course in courses if course.field.slug in reasons], student,
            lambda course: f"You mentioned {join(reasons[course.field.slug][:3])}, which connects to {course.field.name}.",
            f"You mentioned {join(liked[:3])}.",
            weight=lambda course: len(reasons[course.field.slug]),   # fields that match more of what they said come first
        )
    if avoid:
        return options(
            [course for course in courses if course.field.slug not in avoid], student,
            lambda course: f"{course.field.name} doesn't depend on what you said you find hard.",
            "Struggling with one subject doesn't close every door. Here are paths that lean on other strengths.",
        )
    if words & {"options", "option", "suggest", "after", "confused", "which", "what", "help", "course", "courses", "career", "careers", "future"}:
        if student.subject_ids is None:
            return Reply(
                "ask_background",
                "I can help with that. First, choose your Class 12 stream or subjects above, so I only show paths that fit. Then tell me what you enjoy.",
                [], ["I like coding", "I like helping people", "I like drawing", "I like business"],
            )
        return options(
            courses, student, lambda course: f"Your subjects leave this {course.field.name} path open.",
            "Here's a wide view from different fields.",
        ) if words & {"options", "option", "after", "suggest", "course", "courses", "career", "careers", "future", "confused"} else unknown()
    return unknown()


def unknown() -> Reply:
    return Reply(
        "unknown",
        "I don't have a checked answer for that, and I won't guess. I can talk about courses, entrance exams, career roadmaps, skills and dates in our records.",
        [], ["What can I do after Class 12?", "I like coding", "What is JEE Main?"],
    )
