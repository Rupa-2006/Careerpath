"""
ITI, GNM nursing and integrated teacher education (ITEP), added on 10 November 2026. No imports from content.py.
- ITI trades: from the official Telangana list (iti.telangana.gov.in). Usually joined after Class 8 or 10, so ITI
  pages sit in the Diploma and Polytechnic area as other options.
- GNM: Indian Nursing Council eligibility page. Taken after Class 12.
- ITEP: NCTE, admission through NCET. Taken after Class 12.
- The regular 2-year B.Ed is taken after a degree, not after Intermediate, so it is a step in the Teacher path, not a page.
"""
from datetime import date

CHECKED = date(2026, 11, 10)


def _iti(slug, name, summary, study, careers):
    return {
        "slug": slug, "name": name, "field": "diploma", "kind": "Certificate", "summary": summary, "study": study,
        "duration": "6 months to 2 years, depending on the trade",
        "admission": ("Usually joined after Class 10 (some trades after Class 8), through the state's ITI admissions. "
                      "Telangana: iti.telangana.gov.in. Andhra Pradesh runs its own ITI admissions."),
        "careers": careers, "exams": [], "source": "ts-iti", "checked": CHECKED,
        "criteria": [{
            "label": "Telangana ITI admissions",
            "summary": "Class 10 passed for most trades, or Class 8 passed for a few (such as Welder, Plumber and Dress Making). "
                       "The minimum age was 14 in the 2025 prospectus. Check this year's prospectus.",
            "groups": [], "known": False, "regions": ["TS"], "min_age": 14, "source": "ts-iti",
        }],
    }


OTHER_COURSES = [
    _iti("iti-engineering", "ITI: Engineering trades (Electrician, Fitter, Mechanic and more)",
         "Short, hands-on training for a skilled trade such as electrician, fitter, welder or vehicle mechanic.",
         "Workshop practice in one trade, safety, trade theory and basic maths and drawing.",
         ["Electrician", "Fitter", "Mechanic"]),
    _iti("iti-non-engineering", "ITI: Non-engineering trades (Computer, Health, Fashion and more)",
         "Short, hands-on training for jobs such as computer operator, health technician or tailor.",
         "Practical skills in one trade, such as computers, health care, sewing or office work.",
         ["Computer Operator", "Health Technician", "Tailor"]),
    {
        "slug": "gnm", "name": "GNM (General Nursing and Midwifery)", "field": "medical", "kind": "Diploma",
        "summary": "A nursing diploma to care for patients in hospitals and communities.",
        "study": "Nursing care, the human body, community health, midwifery and hospital practice.",
        "duration": "3 years", "admission": "Through your state's nursing admission notice. Check the notice for this year.",
        "careers": ["Staff Nurse", "Community Health Nurse"], "exams": [], "source": "inc-elig", "checked": CHECKED,
        "criteria": [{
            "label": "All India (Indian Nursing Council)",
            "summary": "Class 12 with English, with at least 40% in English and 40% overall. Science is preferred. "
                       "Age 17 to 35 on 31 December of the admission year. Registered ANMs can also apply.",
            "groups": [(1, ["english"])], "min_percentage": 40, "min_percentage_reserved": 40, "min_age": 17, "max_age": 35,
            "source": "inc-elig",
        }],
    },
    {
        "slug": "itep", "name": "ITEP: Integrated B.A., B.Sc. or B.Com. with B.Ed (4 years)", "field": "arts", "kind": "Degree",
        "summary": "A 4-year course that gives a degree and a teaching degree (B.Ed) together.",
        "study": "Your main subject, how children learn, teaching methods and school internships.",
        "duration": "4 years", "admission": "Through NCET, the national entrance test run by NTA for ITEP.",
        "careers": ["School Teacher"], "exams": [], "source": "ncte-itep", "checked": CHECKED,
        "criteria": [{
            "label": "All India (NCTE)",
            "summary": "Class 12 or equivalent with at least 50% marks in aggregate. Check this year's NCET bulletin for any changes.",
            "groups": [], "min_percentage": 50, "min_percentage_reserved": 50, "source": "ncte-itep",
        }],
    },
]

OTHER_SOURCES = {
    "ts-iti": ("Telangana ITI admissions: list of trades", "https://iti.telangana.gov.in/list-of-trades"),
    "inc-elig": ("Indian Nursing Council: eligibility criteria", "https://indiannursingcouncil.org/eligibility-criteria"),
    "ncte-itep": ("NCTE: Integrated Teacher Education Programme", "https://ncte.gov.in/website/ITEP/ITEPDocument.aspx"),
}

OTHER_ROADMAPS = {
    "iti-engineering": ["vocational-professional", "electrical-engineer"],
    "iti-non-engineering": ["vocational-professional"],
    "gnm": ["nurse"],
    "itep": ["teacher"],
}

OTHER_NOTES = {
    "iti-engineering": (2, "ITI is short and practical. Do the steps that build your trade skill, and think about a diploma or apprenticeship later."),
    "iti-non-engineering": (2, "ITI is short and practical. Do the steps that build your trade skill, and get a recognised certificate."),
    "gnm": (3, "GNM is a 3-year nursing diploma. You can study B.Sc Nursing later (Post Basic) if you want to go further."),
    "itep": (4, "Your course gives a degree and B.Ed together, so school internships are a big part of it."),
}
