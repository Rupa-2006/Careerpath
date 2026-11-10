"""
Polytechnic diploma pages, added on 10 November 2026. Branch names come from the official lists:
Telangana SBTET "Courses" page (40 branches) and the AP SBTET Diploma Curriculum C-20 page (27 branches).
Polytechnic diplomas are usually joined after Class 10 through POLYCET, so the site keeps them in the
"Diploma and Polytechnic" area as other options, not alongside degrees.
"""
from datetime import date

LATER_CHECK = date(2026, 11, 5)   # same review date as the other newer courses; no import, so nothing loads in a circle

POLY_ADMISSION = ("Usually joined after Class 10 (SSC) through POLYCET, in Andhra Pradesh and Telangana. "
                  "After the diploma, you can join B.Tech in the second year through ECET (lateral entry).")
POLY_RULE = {
    "label": "AP and Telangana (POLYCET)",
    "summary": "For students who have passed Class 10 (SSC) or an equivalent exam. Check this year's POLYCET notification "
               "for marks, age and local-area rules.",
    "groups": [], "known": False, "source": "sbtet-ts",
}


def _poly(slug, name, summary, study, careers):
    return {
        "slug": slug, "name": name, "field": "diploma", "kind": "Diploma", "summary": summary, "study": study,
        "duration": "3 years (some branches are 3½ years with industrial training)", "admission": POLY_ADMISSION,
        "careers": careers, "exams": ["ap-ecet", "tg-ecet"], "source": "sbtet-ts", "criteria": [POLY_RULE], "checked": LATER_CHECK,
    }


DIPLOMAS = [
    _poly("dip-civil", "Diploma in Civil Engineering (Polytechnic)",
          "A practical diploma about building roads, buildings and water works.",
          "Surveying, building materials, drawing, construction and estimating.",
          ["Site Supervisor", "Junior Engineer"]),
    _poly("dip-mech", "Diploma in Mechanical Engineering (Polytechnic)",
          "A practical diploma about machines, manufacturing and vehicles.",
          "Workshop practice, machine drawing, manufacturing, engines and maintenance.",
          ["Technician", "Production Supervisor"]),
    _poly("dip-electrical", "Diploma in Electrical and Electronics Engineering (Polytechnic)",
          "A practical diploma about electric power, wiring, motors and electric vehicles.",
          "Circuits, wiring, electrical machines, power systems and safety.",
          ["Electrical Technician", "Junior Engineer"]),
    _poly("dip-electronics", "Diploma in Electronics Engineering (Polytechnic)",
          "A practical diploma about electronic circuits, communication and instruments.",
          "Electronic circuits, communication, instruments, embedded systems and repair.",
          ["Electronics Technician", "Service Engineer"]),
    _poly("dip-computer", "Diploma in Computer Engineering (Polytechnic)",
          "A practical diploma about computers, programming, networks and the web.",
          "Programming, web design, networks, databases and computer hardware.",
          ["Junior Programmer", "Computer Technician"]),
    _poly("dip-chemical", "Diploma in Chemical Technology (Polytechnic)",
          "A practical diploma about chemical, plastic, sugar, ceramic and oil plants.",
          "Chemistry, plant operations, process control, testing and safety.",
          ["Plant Operator", "Lab Technician"]),
    _poly("dip-mining", "Diploma in Mining and Metallurgy (Polytechnic)",
          "A practical diploma about working in mines and metal plants.",
          "Mine surveying, mining machines, metal testing and safety.",
          ["Mine Supervisor", "Metallurgy Technician"]),
    _poly("dip-textile", "Diploma in Textile, Garment and Leather Technology (Polytechnic)",
          "A practical diploma about making fabrics, clothes, leather goods and footwear.",
          "Spinning, weaving, garment making, leather work, fashion basics and quality.",
          ["Production Supervisor", "Fashion Technician"]),
    _poly("dip-design", "Diploma in Design, Printing and Animation (Polytechnic)",
          "A practical diploma in architecture drawing, interior or landscape design, printing or animation.",
          "Drawing, design software, printing, packaging and animation.",
          ["Draughtsperson", "Design Assistant", "Animator"]),
    _poly("dip-commerce", "Diploma in Commercial and Computer Practice (Polytechnic)",
          "A practical diploma about office work, accounts and computers.",
          "Accounts, office work, typing, computer applications and business basics.",
          ["Office Assistant", "Accounts Assistant"]),
    _poly("dip-home-science", "Diploma in Home Science (Polytechnic)",
          "A practical diploma about food, nutrition, clothing and home management.",
          "Food and nutrition, textiles, child care and home management.",
          ["Nutrition Assistant", "Childcare Worker"]),
]

DIPLOMA_ROADMAPS = {
    "dip-civil": ["civil-engineer"], "dip-mech": ["mechanical-engineer"], "dip-electrical": ["electrical-engineer"],
    "dip-electronics": ["embedded-engineer"], "dip-computer": ["web-developer"], "dip-chemical": ["chemical-engineer"],
    "dip-mining": ["mining-metallurgy-engineer"], "dip-textile": ["designer"], "dip-design": ["designer", "architect"],
    "dip-commerce": ["accounts-finance", "business-manager"], "dip-home-science": ["health-technologist"],
}

DIPLOMA_NOTE = ("Your diploma takes about 3 years. You can start working as a technician, or join B.Tech in the "
                "second year through ECET. Follow the steps that match your level.")
DIPLOMA_NOTES = {slug: (3, DIPLOMA_NOTE) for slug in DIPLOMA_ROADMAPS}

# Official branch names -> page. TS from the SBTET Courses page; AP from the SBTET C-20 curriculum page.
TS_BRANCHES = {
    "ARCHITECTURAL ASSISTANTSHIP": "dip-design", "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING": "dip-computer",
    "Aircraft Maintenance Engineering": "dip-mech", "Advanced Manufacturing Technology": "dip-mech",
    "Automation & robotics": "dip-mech", "AUTOMOBILE ENGINEERING": "dip-mech", "BIOMEDICAL ENGINEERING": "dip-electronics",
    "Bio technology": "dip-chemical", "Computer Application and Business Management": "dip-commerce",
    "Civil Engineering(Building services Engineering)": "dip-civil", "CLOUD COMPUTING AND BIG DATA": "dip-computer",
    "COMMERCIAL AND COMPUTER PRACTICE": "dip-commerce", "CIVIL ENGINEERING": "dip-civil", "CHEMICAL ENGINEERING": "dip-chemical",
    "CYBER PHYSICAL SYSTEMS AND SECURITY": "dip-computer", "Civil Engineering, Real Estate and Valuation": "dip-civil",
    "COMPUTER SCIENCE AND ENGINEERING": "dip-computer", "Construction Technology and management": "dip-civil",
    "ELECTRONICS & COMMUNICATION ENGINEERING": "dip-electronics", "ELECTRICAL AND ELECTRONICS ENGINEERING": "dip-electrical",
    "Electrical Engineering and Electric Vehicle Technology": "dip-electrical", "ELECTRONICS AND INSTRUMENTATION ENGINEERING": "dip-electronics",
    "EMBEDDED SYSTEMS": "dip-electronics", "ELECTRONICS AND VIDEO ENGINEERING": "dip-electronics", "HOME SCIENCE": "dip-home-science",
    "Interior Design": "dip-design", "Landscape Design": "dip-design", "LEATHER AND FASHION TECHNOLOGY": "dip-textile",
    "LEATHER GOODS & FOOTWEAR TECHNOLOGY": "dip-textile", "MECHANICAL ENGINEERING": "dip-mech",
    "Multimedia and Electronics Engineering": "dip-electronics", "MINING ENGINEERING": "dip-mining",
    "METALLURGICAL ENGINEERING": "dip-mining", "Printing Technology and Data analytics": "dip-design", "PHARMACY": "d-pharm",
    "PACKAGING TECHNOLOGY": "dip-chemical", "PRINTING TECHNOLOGY": "dip-design", "Semiconductor Technology": "dip-electronics",
    "Textile and Fashion Technology": "dip-textile", "TEXTILE TECHNOLOGY": "dip-textile",
}
AP_BRANCHES = {
    "DIPLOMA IN CHEMICAL ENGINEERING": "dip-chemical", "DIPLOMA IN CHEMICAL ENGINEERING (PETROCHEMICALS)": "dip-chemical",
    "DIPLOMA IN CHEMICAL ENGINEERING (PLASTICS AND POLYMERS)": "dip-chemical", "DIPLOMA IN ARCHITECTURAL ASSISTANTSHIP": "dip-design",
    "DIPLOMA IN AUTOMOBILE ENGINEERING": "dip-mech", "DIPLOMA IN WEB DESIGNING": "dip-computer",
    "DIPLOMA IN APPLIED ELECTRONICS AND INSTRUMENTATION ENGINEERING": "dip-electronics",
    "DIPLOMA IN ANIMATION AND MULTIMEDIA ENGINEERING": "dip-design", "DIPLOMA IN MINING ENGINEERING": "dip-mining",
    "DIPLOMA IN PETROLEUM TECHNOLOGY": "dip-chemical", "DIPLOMA IN BIOMEDICAL ENGINEERING": "dip-electronics",
    "DIPLOMA IN CIVIL ENGINEERING": "dip-civil", "DIPLOMA IN COMPUTER SCIENCE ENGINEERING (ARTIFICIAL INTELLIGENCE)": "dip-computer",
    "DIPLOMA IN COMMERCIAL AND COMPUTER PRACTICE": "dip-commerce", "DIPLOMA IN CERAMIC TECHNOLOGY": "dip-chemical",
    "DIPLOMA IN COMPUTER ENGINEERING": "dip-computer", "DIPLOMA IN 3D ANIMATION AND GRAPHICS ENGINEERING": "dip-design",
    "DIPLOMA IN ELECTRONICS & COMMUNICATION ENGINEERING": "dip-electronics", "DIPLOMA IN ELECTRICAL & ELECTRONICS ENGINEERING": "dip-electrical",
    "DIPLOMA COURSE IN PHARMACY": "d-pharm", "DIPLOMA IN GARMENT TECHNOLOGY": "dip-textile", "DIPLOMA IN MECHANICAL ENGINEERING": "dip-mech",
    "DIPLOMA IN METALLURGICAL ENGINEERING": "dip-mining", "DIPLOMA IN CHEMICAL ENGINEERING (SUGAR TECHNOLOGY)": "dip-chemical",
    "DIPLOMA IN TEXTILE TECHNOLOGY": "dip-textile",
}

SMALL = {"And", "Of", "In", "For"}


def nice(name: str) -> str:
    """'DIPLOMA IN CIVIL ENGINEERING' -> 'Diploma in Civil Engineering'. Names already in mixed case keep their case."""
    if not name.isupper():
        return name
    words = name.replace("&", "and").title().split()
    return " ".join(word.lower() if word in SMALL and index else word for index, word in enumerate(words)).replace("3D", "3D")


# Rows for the full course list: (name, group, duration, state, route, course page, source)
DIPLOMA_LIST = (
    [(f"Diploma in {nice(name)}", "Polytechnic Diploma", "3 years", "TS", "TS POLYCET", slug, "sbtet-ts") for name, slug in TS_BRANCHES.items()]
    + [(nice(name), "Polytechnic Diploma", "3 years", "AP", "AP POLYCET", slug, "sbtet-ap") for name, slug in AP_BRANCHES.items()]
)
