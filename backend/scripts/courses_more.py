"""
Course pages for the official degree, integrated and other courses that had no page yet, added on 10 November 2026.
Each official name on the AP (OAMDC, EAPCET, LAWCET) and Telangana (DOST, KNRUHS) lists is linked to one of these
pages, or to an existing page, in courses_links.py. Degree-college courses keep no subject rule, like B.Sc Computer
Science and BA, because DOST and OAMDC rules differ by college and combination.
"""
from scripts.content import LATER_CHECK, _ayush

DEGREE_ADMISSION = ("Through DOST in Telangana and OAMDC in Andhra Pradesh, based on your Intermediate marks. "
                    "Some central universities use CUET (UG).")
DEGREE_YEARS = "3 years, or 4 years for an Honours degree"


def _degree(slug, name, field, summary, study, careers, source="cap", **extra):
    return {
        "slug": slug, "name": name, "field": field, "kind": "Degree", "summary": summary, "study": study,
        "duration": DEGREE_YEARS, "admission": DEGREE_ADMISSION, "careers": careers, "exams": ["cuet-ug"],
        "source": source, "criteria": [], "checked": LATER_CHECK, **extra,
    }


LAW_5_YEAR = [
    {"label": "Andhra Pradesh (AP LAWCET, 2025 booklet)", "summary": "Intermediate with at least 45% for OC, 42% for BC and 40% for SC/ST candidates.",
     "groups": [], "min_percentage": 45, "min_percentage_reserved": 40, "regions": ["AP"], "source": "lawcet"},
    {"label": "National Law Universities (CLAT)", "summary": "Class 12 or equivalent, with at least 45% marks (40% for SC, ST and PwD). There is no upper age limit.",
     "groups": [], "min_percentage": 45, "min_percentage_reserved": 40, "source": "clat-ug"},
]

MORE_COURSES = [
    # ---- Science degrees
    _degree("bsc-physical", "B.Sc Physical Sciences (Maths, Physics, Chemistry)", "science",
            "A science degree in maths, physics, chemistry and related subjects such as statistics.",
            "Maths, physics, chemistry, and lab work. Some colleges offer quantum or material science.",
            ["Teacher", "Research Assistant", "Data Analyst"], source="dost"),
    _degree("bsc-life", "B.Sc Life Sciences (Botany, Zoology, Chemistry)", "science",
            "A science degree about plants, animals and the chemistry of life.",
            "Botany, zoology, chemistry, microbiology, genetics and lab work.",
            ["Teacher", "Lab Analyst", "Research Assistant"], source="dost"),
    _degree("bsc-chemistry", "B.Sc Chemistry", "science",
            "A science degree focused on chemistry, used in medicine, food, cement and chemical factories.",
            "Organic, inorganic, physical and analytical chemistry, lab testing and quality control.",
            ["Lab Chemist", "Quality Control Analyst"]),
    _degree("bsc-biotech", "B.Sc Biotechnology and Bioinformatics", "science",
            "A science degree about using living cells, and computers, to study and make useful products.",
            "Cell biology, genetics, microbiology, biotechnology methods and bioinformatics.",
            ["Lab Technician", "Research Assistant"]),
    _degree("bsc-data", "B.Sc Data Science and Artificial Intelligence", "science",
            "A science degree about working with data, statistics and AI.",
            "Statistics, programming, data analysis, machine learning and AI basics.",
            ["Data Analyst", "AI Assistant Engineer"]),
    _degree("bsc-cyber", "B.Sc Cyber Security and Digital Forensics", "science",
            "A science degree about protecting computers and investigating digital crimes.",
            "Networks, operating systems, security, digital forensics and cyber law basics.",
            ["Security Analyst", "Digital Forensics Assistant"]),
    _degree("bsc-electronics", "B.Sc Electronics", "science",
            "A science degree about electronic circuits, devices and embedded systems.",
            "Circuits, digital electronics, microcontrollers, IoT and electronic manufacturing.",
            ["Electronics Technician", "Embedded Developer"]),
    _degree("bsc-earth", "B.Sc Geology and Earth Sciences", "science",
            "A science degree about rocks, minerals, the earth and the land.",
            "Geology, mineralogy, geophysics, geochemistry, maps and fieldwork.",
            ["Geologist", "Field Survey Assistant"], source="dost"),
    _degree("bsc-environment", "B.Sc Environmental Science", "science",
            "A science degree about nature, pollution, climate and clean energy.",
            "Ecology, pollution control, climate science, renewable energy and environment laws.",
            ["Environment Officer", "Sustainability Assistant"], source="dost"),
    _degree("bsc-nutrition", "B.Sc Food Science and Nutrition", "science",
            "A science degree about food, healthy eating and food safety.",
            "Nutrition, food chemistry, diet planning, food processing and food safety.",
            ["Nutritionist", "Food Quality Officer"]),
    _degree("bsc-aqua", "B.Sc Aquaculture and Fisheries", "science",
            "A science degree about farming fish and prawns, and caring for water life.",
            "Fish biology, pond management, water quality, fish health and hatcheries.",
            ["Aquaculture Supervisor", "Hatchery Technician"]),
    _degree("bsc-psychology", "B.Sc Psychology", "science",
            "A science degree about how people think, feel and behave.",
            "Human behaviour, development, counselling basics, research methods and statistics.",
            ["Counselling Assistant", "HR Assistant"]),
    _degree("bsc-forensic", "B.Sc Forensic Science", "science",
            "A science degree about using science to help solve crimes.",
            "Crime-scene science, chemistry, biology, fingerprints and lab testing.",
            ["Forensic Lab Assistant", "Lab Analyst"]),
    _degree("bsc-agri-studies", "B.Sc Agricultural and Allied Sciences (degree colleges)", "agriculture",
            "A degree-college science course about farming, rural development, dairy, silk farming or forests.",
            "Crop and soil basics, organic farming, sericulture, dairy and poultry, and rural development.",
            ["Farm Supervisor", "Rural Development Assistant"]),
    {
        **_degree("bsc-bed", "B.Sc B.Ed (integrated teacher education)", "science",
                  "A 4-year course that gives a science degree and a teaching degree together.",
                  "Science subjects, how children learn, teaching methods and school internships.",
                  ["School Teacher"], source="dost"),
        "duration": "4 years",
    },
    # ---- Design and performing arts
    _degree("bsc-animation", "B.Sc Animation and Multimedia", "design",
            "A degree about animation, graphics, games and visual communication.",
            "Drawing, 2D and 3D animation, graphic design, video editing and game art.",
            ["Animator", "Graphic Designer"]),
    _degree("bsc-design", "B.Sc Fashion and Design Technology", "design",
            "A degree about designing clothes and products, and how they are made.",
            "Fashion design, textiles, pattern making, design software and marketing.",
            ["Fashion Designer", "Product Design Assistant"], source="dost"),
    _degree("bpa", "BPA (Bachelor of Performing Arts: Music and Dance)", "arts",
            "A degree in music or classical dance, such as vocal, veena, violin or Bharatanatyam.",
            "Performance practice, music or dance theory, history and stage work.",
            ["Performing Artist", "Music or Dance Teacher"]),
    # ---- Law, health, pharmacy
    {
        "slug": "int-llb", "name": "BBA LL.B and B.Com LL.B (5-year integrated law)", "field": "law", "kind": "Degree",
        "summary": "A 5-year law degree joined with business (BBA) or commerce (B.Com).",
        "study": "Law subjects, moot courts, and business or commerce subjects.",
        "duration": "5 years", "admission": "Through AP LAWCET in Andhra Pradesh, or CLAT for National Law Universities.",
        "careers": ["Advocate", "Corporate Legal Executive"], "exams": ["ap-lawcet", "clat"], "source": "lawcet",
        "criteria": LAW_5_YEAR, "checked": LATER_CHECK,
    },
    {   # Siddha is not taught at KNRUHS, so the Telangana note from the helper is replaced
        **_ayush("bsms", "BSMS (Siddha Medicine and Surgery)", "A professional degree in Siddha medicine.",
                 "Siddha medicine and how to treat patients.", ["Siddha Doctor"], "4½ years, plus 1 year"),
        "duration": "4½ years, plus 1 year internship",
    },
    {
        "slug": "d-pharm", "name": "D.Pharm (Diploma in Pharmacy)", "field": "pharmacy", "kind": "Diploma",
        "summary": "A 2-year diploma to work as a pharmacist in a medical shop or hospital.",
        "study": "Medicines, how they work, dispensing, and pharmacy rules.",
        "duration": "2 years", "admission": "Rules differ by state. Check the official notice for this year.",
        "careers": ["Pharmacist (registered)", "Pharmacy Assistant"], "exams": [], "source": "pci",
        "criteria": [], "checked": LATER_CHECK,
    },
]
