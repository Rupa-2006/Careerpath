"""
More B.Tech branches, added on 10 November 2026. Every name below is on an official AP or Telangana counselling list
(see course_list_data.py: AP CAP portal and the TG ECET list). Branches offered in only one state keep only that state's
exams and rules. Biotechnology and Biomedical are left out for now, because in Telangana they are admitted through
the BiPC stream and need their own eligibility rules.
"""
from scripts.content import ENGINEERING_RULE, ENGINEERING_TS, LATER_CHECK, _btech

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
