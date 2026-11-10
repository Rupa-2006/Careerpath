"""
More B.Tech branches, added on 10 November 2026. Every name below is on an official AP or Telangana counselling list
(see course_list_data.py: AP CAP portal and the TG ECET list). Branches offered in only one state keep only that state's
exams and rules. Biotechnology and Biomedical are left out for now, because in Telangana they are admitted through
the BiPC stream and need their own eligibility rules.
"""
from scripts.content import ENGINEERING_AP, ENGINEERING_RULE, ENGINEERING_TS, LATER_CHECK, _btech

AP_ONLY = {"exams": ["jee-main", "jee-advanced", "ap-eapcet", "ap-ecet"], "criteria": [ENGINEERING_RULE, ENGINEERING_AP]}
TS_ONLY = {"exams": ["jee-main", "jee-advanced", "tg-eapcet", "tg-ecet"], "criteria": [ENGINEERING_RULE, ENGINEERING_TS]}

MORE_ENGINEERING = [
    _btech("btech-ai", "B.Tech Artificial Intelligence",
           "An engineering degree about building computer systems that can learn, reason and make decisions.",
           "Programming, maths, machine learning, deep learning and AI projects.",
           ["AI Engineer", "Machine Learning Engineer"], checked=LATER_CHECK),
    _btech("btech-csbs", "B.Tech Computer Science and Business Systems",
           "An engineering degree that mixes computer science with how businesses work.",
           "Programming, databases, business basics, accounts and management.",
           ["Software Developer", "Business Analyst"], checked=LATER_CHECK),
    _btech("btech-cs-design", "B.Tech Computer Science and Design",
           "An engineering degree that mixes computer science with design, such as apps, games and user experience.",
           "Programming, user interface design, graphics and design thinking.",
           ["UI/UX Designer", "Front-end Developer"], checked=LATER_CHECK, **TS_ONLY),
    _btech("btech-cse-iot", "B.Tech CSE (Internet of Things)",
           "An engineering degree about connecting everyday devices to the internet and to each other.",
           "Programming, electronics basics, sensors, networks and IoT projects.",
           ["IoT Engineer", "Embedded Software Engineer"], checked=LATER_CHECK),
    _btech("btech-eie", "B.Tech Electronics and Instrumentation Engineering",
           "An engineering degree about instruments that measure and control machines and factories.",
           "Electronics, sensors, measurement, control systems and automation.",
           ["Instrumentation Engineer", "Control Systems Engineer"], checked=LATER_CHECK),
    _btech("btech-robotics", "B.Tech Automation and Robotics",
           "An engineering degree about designing and programming robots and automatic machines.",
           "Mechanics, electronics, programming, sensors and robot control.",
           ["Robotics Engineer", "Automation Engineer"], checked=LATER_CHECK, **TS_ONLY),
    _btech("btech-automobile", "B.Tech Automobile Engineering",
           "An engineering degree about designing, building and servicing vehicles.",
           "Engines, vehicle design, electric vehicles, manufacturing and testing.",
           ["Automobile Engineer", "EV Engineer"], checked=LATER_CHECK),
    _btech("btech-aeronautical", "B.Tech Aeronautical Engineering",
           "An engineering degree about designing, building and maintaining aircraft.",
           "Aerodynamics, aircraft structures, propulsion and materials.",
           ["Aeronautical Engineer", "Aircraft Maintenance Engineer"], checked=LATER_CHECK, **TS_ONLY),
    _btech("btech-chemical", "B.Tech Chemical Engineering",
           "An engineering degree about turning raw materials into useful products safely, in factories and plants.",
           "Chemistry, process design, heat and mass transfer, plant safety and control.",
           ["Process Engineer", "Plant Engineer"], checked=LATER_CHECK),
]


# Added later on 10 November 2026: the rest of the official branches that need a page of their own.
# For branches that also take BiPC students, the full 2026 rules were not confirmed on official pages,
# so they carry only the confirmed subject rule below, not marks or age.
MIXED_ADMISSION = ("Through AP EAPCET or TG EAPCET. Depending on the university, some seats are for MPC students and some "
                   "for BiPC students. Check the official booklet for this year.")
# The part every official source agrees on: these branches take MPC or BiPC students, so Physics and Chemistry
# are needed, plus Maths or Biology. Marks, age and which group gets seats are left to the official booklet.
MPC_OR_BIPC = {
    "label": "AP and Telangana (MPC or BiPC)",
    "summary": "You need Intermediate with Physics and Chemistry, plus Maths (MPC) or Biology (BiPC). Which group gets seats, "
               "and the marks and age rules, depend on the university, so check this year's official booklet.",
    "groups": [(1, ["physics"]), (1, ["chemistry"]), (1, ["mathematics", "biology"])],
    "source": "tg-eapcet-ap",
}
MIXED = {"exams": ["ap-eapcet", "tg-eapcet"], "criteria": [MPC_OR_BIPC], "admission": MIXED_ADMISSION}

MORE_ENGINEERING += [
    _btech("btech-mining", "B.Tech Mining Engineering",
           "An engineering degree about finding and safely taking out coal, metals and minerals from the earth.",
           "Geology, mine planning, rock mechanics, mine safety and machinery.",
           ["Mining Engineer", "Mine Safety Officer"], checked=LATER_CHECK),
    _btech("btech-metallurgy", "B.Tech Metallurgical Engineering",
           "An engineering degree about metals: how they are made, shaped, tested and improved.",
           "Materials science, iron and steel making, heat treatment, testing and corrosion.",
           ["Metallurgical Engineer", "Materials Engineer"], checked=LATER_CHECK),
    _btech("btech-textile", "B.Tech Textile Technology",
           "An engineering degree about making fibres, yarns and fabrics in factories.",
           "Fibre science, spinning, weaving, textile chemistry and quality control.",
           ["Textile Engineer", "Production Manager"], checked=LATER_CHECK, **TS_ONLY),
    _btech("btech-petroleum", "B.Tech Petroleum Engineering",
           "An engineering degree about finding, producing and processing oil and gas.",
           "Geology, drilling, reservoir engineering, refining and safety.",
           ["Petroleum Engineer", "Drilling Engineer"], checked=LATER_CHECK, **AP_ONLY),
    _btech("btech-biotech", "B.Tech Biotechnology",
           "An engineering degree that uses living cells and biology to make medicines, food and other products.",
           "Biology, chemistry, genetics, microbiology and bioprocess engineering.",
           ["Biotechnologist", "Research Assistant"], checked=LATER_CHECK, **MIXED),
    _btech("btech-biomedical", "B.Tech Biomedical Engineering",
           "An engineering degree about medical devices and machines used in hospitals.",
           "Electronics, human body basics, medical instruments and imaging.",
           ["Biomedical Engineer", "Medical Equipment Engineer"], checked=LATER_CHECK, **MIXED),
    _btech("btech-food-tech", "B.Tech Food Technology",
           "An engineering degree about processing, preserving and packing food safely.",
           "Food chemistry, microbiology, food processing, packaging and quality.",
           ["Food Technologist", "Quality Control Officer"], checked=LATER_CHECK, **MIXED),
    _btech("btech-dairy", "B.Tech Dairy Technology",
           "An engineering degree about processing milk and making dairy products.",
           "Milk science, dairy processing, dairy engineering, quality and plant hygiene.",
           ["Dairy Technologist", "Plant Supervisor"], checked=LATER_CHECK, **MIXED),
    _btech("btech-pharma-eng", "B.Tech Pharmaceutical Engineering",
           "An engineering degree about designing and running the plants that make medicines.",
           "Chemistry, pharmaceutics, process engineering, quality and plant design.",
           ["Pharmaceutical Process Engineer", "Quality Engineer"], checked=LATER_CHECK, **MIXED),
    _btech("btech-agri-eng", "B.Tech Agricultural Engineering",
           "An engineering degree about farm machines, irrigation and storing crops.",
           "Farm machinery, soil and water engineering, irrigation and food storage.",
           ["Agricultural Engineer", "Irrigation Engineer"], checked=LATER_CHECK, **MIXED),
]
