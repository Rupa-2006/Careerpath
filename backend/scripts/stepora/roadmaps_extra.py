"""
More steps for the roadmaps that were short, added on 8 November 2026, so each one covers every year.
Same rules as the other roadmap files: general guidance only, no admission rules, fees, salaries or promises.
"""
from .roadmaps import INTERNSHALA, NCS, NPTEL, SWAYAM
from .roadmaps_path import WHO, goal, step
from .roadmaps_path2 import ICAR, ICSI, IGRUA, IISER, KNRUHS, NATA, SSC, UPSC

DGCA = "https://www.dgca.gov.in/"

EXTRA_STEPS = {
    "physiotherapist": [
        step(1, 2, "Learn anatomy with your hands", "Physiotherapy depends on knowing exactly where each muscle and joint is.", SWAYAM,
             "Each week, find and name ten muscles on yourself or a model."),
        step(2, 2, "Practise talking to patients", "Patients do their exercises only when they understand and trust you.", WHO,
             "Explain one exercise to a family member in simple words, then ask what they understood."),
        step(3, 2, "Keep careful patient notes", "Good notes show progress and keep patients safe.", WHO,
             "For every patient you see in training, write what you did and how they responded."),
        step(4, 3, "Learn one special area well", "Sports, neuro, children and older people each need extra skills.", SWAYAM,
             "Choose one area, and finish one short online course in it."),
    ],
    "business-manager": [
        step(1, 3, "Learn to use a computer for work", "Every office uses documents, spreadsheets and email every day.", SWAYAM,
             "Write one formal email and one short report this month."),
        step(2, 3, "Understand marketing and customers", "Every business lives on knowing what customers want.", SWAYAM,
             "Ask ten people why they buy from one shop, and write what you learn."),
        step(3, 2, "Lead a small team project", "Managers are judged by how well their team works.", SWAYAM,
             "Lead one college event or project, and note what went well and what did not."),
        step(3, 3, "Decide between a job and higher study", "Some students work first, and others go for an MBA. Both are fine.", NCS,
             "Talk to two people who chose each path, and write your own reasons."),
    ],
    "architect": [
        step(1, 2, "Learn to see buildings", "Architects learn by studying good and bad spaces around them.", NATA,
             "Sketch one building each week, and write why it feels good or bad to be in."),
        step(2, 2, "Learn about climate and light", "Good buildings stay comfortable without wasting energy.", NPTEL,
             "Notice which rooms in your home get sun and air, and draw a simple plan showing it."),
        step(3, 2, "Make physical models", "Models help you and your clients understand a design.", SWAYAM,
             "Build one simple model from card for a design you drew."),
        step(4, 2, "Learn building rules and site work", "A design must follow local building rules to be built.", NPTEL,
             "Visit one building site, and list three things you learned there."),
    ],
    "researcher": [
        step(1, 2, "Read about science every week", "Researchers keep learning beyond the textbook.", NPTEL,
             "Read one popular science article each week, and write one question it raises."),
        step(2, 2, "Learn to work in a lab safely", "Careful lab habits make results trustworthy.", NPTEL,
             "Keep a neat lab notebook for every experiment, with dates and results."),
        step(3, 2, "Learn to read research papers", "Papers are how scientists share new work.", NPTEL,
             "Read one short paper in your area, and summarise it in one page."),
        step(4, 2, "Do a summer research project", "Short projects help you find what you enjoy.", IISER,
             "Write to one teacher about a summer project, and finish a short report."),
    ],
    "pilot": [
        step(1, 3, "Learn how the aviation rules work", "DGCA sets the licence rules, so read them yourself.", DGCA,
             "Read the DGCA pages about pilot licences, and note the steps you must follow."),
        step(2, 3, "Improve your English radio talk", "Pilots speak with air traffic control in clear English.", SWAYAM,
             "Practise reading aviation phrases aloud for ten minutes a day."),
        step(2, 4, "Learn weather and navigation well", "Most flying decisions depend on weather and route planning.", IGRUA,
             "Read one weather report each day, and explain what it means for flying."),
        step(3, 2, "Keep your medical and licence papers up to date", "Pilots must keep their papers valid to keep flying.", DGCA,
             "Make a list of every document you hold, and when each one needs renewing."),
    ],
    "defence-officer": [
        step(1, 4, "Read newspapers every day", "The interview and tests check what you know about the world.", UPSC,
             "Read one newspaper each day, and write two lines on one important story."),
        step(1, 5, "Practise English and speaking", "Officers must speak and write clearly.", SWAYAM,
             "Speak for two minutes on a topic each day, and record yourself."),
        step(2, 3, "Build leadership in daily life", "The SSB looks for people who lead and help others naturally.", NCS,
             "Take charge of one group task at college, and note how you handled problems."),
        step(2, 4, "Learn about the three services", "Knowing the Army, Navy and Air Force helps you choose and explain your choice.", UPSC,
             "Write one page on why you want the service you chose."),
    ],
    "government-exams": [
        step(1, 4, "Read news every day for general awareness", "Many papers test current events.", SSC,
             "Read one newspaper daily, and keep a short notebook of key events."),
        step(1, 5, "Practise maths without a calculator", "Speed in basic maths saves time in the exam.", SWAYAM,
             "Solve twenty quick maths questions each day, and time yourself."),
        step(2, 3, "Take full mock tests", "Mock tests show your weak areas and build speed.", SSC,
             "Take one timed mock test each week, and study every mistake."),
        step(2, 4, "Keep a backup plan", "Exams have limited posts, so keep a second option ready.", NCS,
             "Register on the National Career Service portal, and look at related jobs."),
    ],
    "vocational-professional": [
        step(1, 3, "Learn workplace safety", "Safe habits protect you and the people you work with.", SWAYAM,
             "List the safety rules for your trade, and follow them every time."),
        step(2, 2, "Learn basic computer and money skills", "Most trades now use phones, billing and online orders.", SWAYAM,
             "Make a simple bill and a price list for one service in your trade."),
        step(2, 3, "Learn from an experienced worker", "Skilled workers teach tricks that books do not.", INTERNSHALA,
             "Spend time with one experienced person in your trade, and note five things they do well."),
        step(3, 3, "Think about starting your own work", "Many trade skills can become a small business.", NCS,
             "Write a one-page plan for a small business in your trade."),
    ],
    "company-secretary": [
        step(1, 3, "Read business news", "Company law changes, and companies make news every day.", SWAYAM,
             "Read one business news story each day, and note which law it relates to."),
        step(2, 2, "Learn to read company documents", "Annual reports and board papers are a company secretary's daily work.", ICSI,
             "Read the annual report of one listed company, and list its main sections."),
        step(3, 2, "Learn computer skills for office work", "Filing, spreadsheets and online forms are part of the job.", SWAYAM,
             "Practise making a neat table and a formal letter on a computer."),
        step(4, 2, "Keep learning after you qualify", "Laws change, so professionals keep studying.", ICSI,
             "Follow ICSI updates each month, and note one change that matters."),
    ],
    "health-technologist": [
        step(1, 2, "Learn medical words", "Reports and requests use medical terms every day.", SWAYAM,
             "Learn ten medical words each week, and use them in sentences."),
        step(2, 3, "Learn to record results carefully", "A small mistake in a report can harm a patient.", WHO,
             "Practise writing neat, complete records during every lab session."),
        step(3, 2, "Learn to talk kindly to patients", "Patients are often worried when they come for tests.", WHO,
             "Explain one test to a family member in simple, calm words."),
        step(4, 2, "Keep up with new equipment", "Machines and methods keep changing.", SWAYAM,
             "Read about one new piece of equipment in your area each month."),
    ],
    "physical-education-teacher": [
        step(1, 4, "Learn how the body works in exercise", "Knowing muscles and breathing helps you train students safely.", SWAYAM,
             "Write a simple warm-up plan, and explain why each part matters."),
        step(1, 5, "Learn to coach one sport well", "Schools value teachers who can build a team.", SWAYAM,
             "Help coach one team or group, and note how each player improves."),
        step(2, 3, "Plan lessons for different ages", "Young children and older students need different activities.", NCS,
             "Write one lesson plan for younger children and one for older students."),
        step(2, 4, "Learn to include every student", "Good PE teachers help students of every ability take part.", SWAYAM,
             "Change one game so a student who finds it hard can still join in."),
    ],
    "animal-and-fisheries": [
        step(1, 2, "Learn to handle animals or fish safely", "Safe handling protects you and the animals.", ICAR,
             "Watch an experienced person at a farm or pond, and note how they handle animals."),
        step(2, 2, "Learn about feed and water quality", "Healthy food and clean water prevent many problems.", ICAR,
             "Write a simple care plan for one animal or one fish pond."),
        step(3, 2, "Learn government schemes for farmers", "Many farmers depend on schemes you can explain to them.", ICAR,
             "List two schemes that help animal or fish farmers, using official pages."),
        step(4, 2, "Keep good records", "Records help find disease early and plan better.", ICAR,
             "Keep a record book for one animal group or pond during your training."),
    ],
    "traditional-medicine-doctor": [
        step(1, 2, "Learn the basic sciences well", "Anatomy and physiology are the base for every system of medicine.", SWAYAM,
             "Draw and label one body system each week."),
        step(2, 2, "Learn your system's classical texts carefully", "Your system has its own principles, which you must know well.", KNRUHS,
             "Make short notes on one topic each week in your own words."),
        step(3, 2, "Learn to keep good patient records", "Records keep patients safe and show what worked.", WHO,
             "For every patient you see in training, write the complaint and the advice given."),
        step(5, 2, "Plan your practice or further study", "Some doctors open a clinic, others join hospitals or study more.", NCS,
             "Talk to two working doctors in your system, and write your own plan."),
    ],
    "social-worker": [
        step(1, 3, "Learn about your local community", "Social workers start by knowing the people they serve.", SWAYAM,
             "Visit one local NGO or community group, and write what problems they work on."),
        step(2, 2, "Learn basic counselling skills", "Many people you meet will be going through hard times.", SWAYAM,
             "Finish one short course on listening or counselling."),
        step(2, 3, "Learn to write reports", "Funding and help often depend on clear reports.", SWAYAM,
             "Write a one-page report on a community problem you saw."),
        step(3, 3, "Choose an area of work", "Child welfare, health, women and rural development each need different skills.", NCS,
             "Pick one area, and find two organisations working in it."),
    ],
}


NMC = "https://www.nmc.org.in/"
INC = "https://www.indiannursingcouncil.org/"
DCI = "https://dciindia.gov.in/"
NCHM = "https://nchm.gov.in/"
CEA = "https://cea.nic.in/"


def term_step(year, semester, position, title, why, resources, build):
    """For roadmaps that are split into semesters."""
    return (year, semester, position, title, "", why, "", resources, build, "")


EXTRA_STEPS |= {
    "doctor": [
        term_step(1, 2, 1, "Learn anatomy by drawing it", "Drawing body parts again and again fixes them in your memory.", NMC,
                  "Draw and label one body part each day, without looking at the book first."),
        term_step(3, 2, 1, "Practise basic clinical skills", "Taking a history and examining a patient are the base of every specialty.", NMC,
                  "In every posting, take one full history and get it checked by a senior."),
        term_step(4, 2, 1, "Learn to read research", "Good doctors check what the evidence says.", WHO,
                  "Read one short medical study each month, and write what it found in two lines."),
    ],
    "nurse": [
        term_step(2, 2, 1, "Learn infection control", "Clean hands and safe habits protect every patient.", WHO,
                  "Follow the hand-washing steps every time, and teach them to one family member."),
        term_step(3, 2, 1, "Learn to keep clear patient records", "Records tell the next nurse what was done.", INC,
                  "Practise writing short, complete notes for every patient you care for in training."),
        term_step(3, 2, 2, "Learn to talk with worried families", "Families trust nurses who explain things calmly.", WHO,
                  "Explain one simple care step to a family member in calm, simple words."),
    ],
    "agriculture-officer": [
        term_step(1, 2, 1, "Learn about water and irrigation", "Water decides what can grow and how much.", "https://icar.org.in/",
                  "Find out how farms near you get water, and write what problems they face."),
        term_step(3, 2, 1, "Learn to use data and apps for farming", "Weather, soil and market apps now guide many farm decisions.", "https://icar.org.in/",
                  "Try one government farm app, and write how it could help a farmer."),
        term_step(3, 2, 2, "Learn about selling and markets", "Farmers earn only when they can sell well.", "https://agriwelfare.gov.in/",
                  "Visit one local market, and note how prices change for one crop."),
    ],
    "civil-engineer": [
        step(1, 2, "Learn engineering drawing", "Drawings are how engineers share their ideas.", NPTEL,
             "Draw one simple building plan by hand each week."),
        step(2, 2, "Learn soil and water basics", "Every structure stands on soil and must handle water.", NPTEL,
             "Find out what kind of soil is in your area, and why it matters for building."),
        step(3, 3, "Learn site safety and estimation", "Engineers must keep workers safe and plan costs.", SWAYAM,
             "List the safety rules on one building site, and estimate the bricks for one small wall."),
    ],
    "electrical-engineer": [
        step(1, 2, "Learn electrical safety", "Electricity can kill, so safe habits come first.", NPTEL,
             "Learn the safety rules for your college lab, and follow them every time."),
        step(2, 3, "Learn electronics and microcontrollers", "Modern electrical systems are controlled by small computers.", NPTEL,
             "Build one small circuit with a microcontroller, such as a light that turns on in the dark."),
        step(4, 2, "Learn about renewable energy", "Solar and wind power are growing fast.", CEA,
             "Read one official report on renewable energy, and note what is changing."),
    ],
    "dentist": [
        step(1, 2, "Learn dental anatomy well", "Every treatment depends on knowing each tooth closely.", DCI,
             "Draw and label one tooth each day until you know them all."),
        step(3, 2, "Follow infection control every time", "Dental tools can spread infection if not cleaned well.", WHO,
             "Learn the cleaning steps for each tool, and follow them without skipping."),
        step(4, 2, "Learn about community dental health", "Many people never visit a dentist, so prevention matters.", WHO,
             "Help in one school or village dental camp, and note what problems you see most."),
    ],
    "designer": [
        step(2, 2, "Learn to research users", "Good design starts by understanding the people who will use it.", SWAYAM,
             "Interview three people about one daily problem, and write what you learn."),
        step(3, 3, "Learn to present your work", "Designers must explain their ideas to clients and teams.", SWAYAM,
             "Present one project to friends in five minutes, and ask for honest feedback."),
        step(4, 2, "Keep up with new tools", "Design tools, including AI tools, change quickly.", SWAYAM,
             "Try one new design tool each month, and note where it helps and where it does not."),
    ],
    "hotel-manager": [
        step(1, 3, "Learn hygiene and grooming", "Guests notice cleanliness first.", NCHM,
             "Follow a daily grooming and hygiene checklist for one month."),
        step(2, 3, "Learn hotel software and bookings", "Hotels run on booking and billing software.", SWAYAM,
             "Practise making a booking and a bill in a spreadsheet."),
        step(3, 3, "Learn to handle complaints", "Calm handling of problems keeps guests coming back.", SWAYAM,
             "Write how you would handle three common guest complaints, and practise with a friend."),
    ],
}


def with_extra_steps(goals: list[dict]) -> list[dict]:
    for goal in goals:
        goal["steps"] = sorted(goal["steps"] + EXTRA_STEPS.get(goal["slug"], []), key=lambda item: (item[0], item[1], item[2]))
    return goals


CHEMICAL = goal("chemical-engineer", "Chemical and Process Engineer", "How to grow from chemistry and maths to running safe chemical plants and processes.", ["btech-chemical"], [
    step(1, 1, "Build your chemistry and maths base", "Every chemical engineering subject uses chemistry and maths.", NPTEL,
         "Solve one chemistry or maths problem each day, and keep your solutions in a notebook."),
    step(1, 2, "Learn lab safety and good habits", "Chemicals can be dangerous, so safe habits come first.", NPTEL,
         "Learn the safety signs and rules in your college lab, and follow them every time."),
    step(2, 1, "Learn how materials and energy move in a process", "Material and energy balances are the core of this field.", NPTEL,
         "Draw the steps of one everyday process, such as making tea or soap, with inputs and outputs."),
    step(2, 2, "Learn heat and mass transfer", "Most plant equipment heats, cools, mixes or separates things.", NPTEL,
         "Find out how a pressure cooker or refrigerator works, and explain the heat flow."),
    step(3, 1, "Learn process design and simulation tools", "Engineers plan plants on computers before building them.", NPTEL,
         "Try one free process simulation tutorial, and design a very small process."),
    step(3, 2, "Get industry experience", "Plant visits and internships show how real factories run.", INTERNSHALA,
         "Do one internship or plant visit, and note three things that surprised you."),
    step(4, 1, "Learn plant safety and environment rules", "Safe, clean operation is a legal and moral duty.", NPTEL,
         "Read about one major industrial accident, and list what went wrong and how it could be prevented."),
    step(4, 2, "Finish a strong project and prepare for jobs", "A focused project shows what you can do.", NCS,
         "Finish a final-year project, make a one-page resume, and practise interviews."),
])

IBM = "https://ibm.gov.in/"
MINING = goal("mining-metallurgy-engineer", "Mining and Metallurgy Engineer", "How to grow from science basics to working safely in mines and metal plants.", ["btech-mining", "btech-metallurgy"], [
    step(1, 1, "Build your maths, physics and chemistry base", "Mines and metal plants are run on these subjects.", NPTEL,
         "Solve one problem from each subject every day, and keep a notebook."),
    step(1, 2, "Learn safety first", "Mines and furnaces are dangerous, so safe habits come before everything else.", NPTEL,
         "Learn the safety signs and rules in your college workshop, and follow them every time."),
    step(2, 1, "Learn rocks, minerals and materials", "You must know what you are digging or melting.", NPTEL,
         "Collect five rock or metal samples, and write what each is and where it is used."),
    step(2, 2, "Learn how ores become metals", "This links mining to metallurgy and to real industry.", IBM,
         "Draw the steps from ore to finished steel or aluminium."),
    step(3, 1, "Learn the machines and plants", "Engineers plan and look after big equipment.", NPTEL,
         "Pick one machine, such as a crusher or furnace, and explain how it works."),
    step(3, 2, "Visit or train at a mine or metal plant", "Site training shows how real operations run.", INTERNSHALA,
         "Do one industrial training, and keep a short daily diary of what you saw."),
    step(4, 1, "Learn environment and mine rules", "Mining and metal work must follow strict rules and protect nature.", IBM,
         "Read the Indian Bureau of Mines website, and list three rules that affect your work."),
    step(4, 2, "Finish a project and prepare for jobs", "A focused project shows what you can do.", NCS,
         "Finish a final-year project, make a one-page resume, and practise interviews."),
])

NCTE = "https://ncte.gov.in/"
SANGEET = "https://www.sangeetnatak.gov.in/"
TEACHER = goal("teacher", "School Teacher", "How to grow from your degree to teaching in a school, step by step.", ["bsc-bed"], [
    step(1, 1, "Master your own subjects", "You can only teach well what you understand deeply.", SWAYAM,
         "Explain one topic each week to a younger student, and see where they get confused."),
    step(1, 2, "Learn how children learn", "Good teachers plan for different kinds of learners.", SWAYAM,
         "Watch one free course lesson on child development, and write three ideas you will use."),
    step(2, 1, "Practise speaking in front of a group", "Teaching is clear speaking, every day.", SWAYAM,
         "Teach a 10-minute lesson to friends, and ask what was clear and what was not."),
    step(2, 2, "Volunteer to teach", "Real classrooms teach you more than books.", NCS,
         "Volunteer at a school, tuition centre or NGO for a few hours each week."),
    step(3, 1, "Learn the teaching qualification rules", "Schools need recognised teaching degrees, and NCTE sets the rules.", NCTE,
         "Read the NCTE website, and note which teaching degree you need, such as a B.Ed."),
    step(3, 2, "Learn to use digital teaching tools", "Schools now use slides, videos and online tests.", SWAYAM,
         "Make one short lesson with slides and a 5-question online quiz."),
    step(4, 1, "Prepare for teacher eligibility tests", "Government and many private schools ask for a teacher eligibility test.", NCS,
         "Find this year's official notice for the teacher test you need, and make a study plan."),
    step(4, 2, "Build your teaching portfolio", "Lesson plans and feedback show schools what you can do.", NCS,
         "Collect your best lesson plans and student feedback in one folder."),
])
LAB = goal("lab-analyst", "Lab and Quality Analyst", "How to grow from science lab work to testing quality in factories and labs.", [], [
    step(1, 1, "Build careful lab habits", "Accurate, safe lab work is the core of this job.", NPTEL,
         "Keep a neat lab notebook for every practical, with dates, readings and results."),
    step(1, 2, "Learn lab safety", "Chemicals and samples can be dangerous.", NPTEL,
         "Learn the safety signs and the right way to handle and throw away chemicals in your lab."),
    step(2, 1, "Learn common testing methods", "Most labs use the same basic tests and instruments.", NPTEL,
         "Pick one instrument in your lab, and write how it works and what it measures."),
    step(2, 2, "Learn how to record and report results", "A test is useful only if others can trust the record.", SWAYAM,
         "Write a one-page report of one experiment, with a clear table and conclusion."),
    step(3, 1, "Learn quality rules and standards", "Factories follow standards to keep products safe.", "https://www.bis.gov.in/",
         "Find one Indian Standard for a product you use, and list what it tests."),
    step(3, 2, "Get lab or factory experience", "Internships show how real quality labs work.", INTERNSHALA,
         "Do one internship in a testing lab, hospital lab or factory quality department."),
    step(4, 1, "Learn the software labs use", "Labs now store results in spreadsheets and lab software.", SWAYAM,
         "Make a spreadsheet that records test results and flags values outside the limits."),
    step(4, 2, "Prepare for jobs or higher study", "Decide between a job now and an M.Sc first.", NCS,
         "Make a one-page resume, and list three labs or companies you would like to work for."),
])
PERFORMER = goal("performing-artist", "Performing Artist (Music and Dance)", "How to grow as a musician or dancer, from daily practice to performing and teaching.", ["bpa"], [
    step(1, 1, "Practise every day", "Skill in music and dance comes from steady daily practice.", SANGEET,
         "Keep a practice diary, and practise at the same time every day for a month."),
    step(1, 2, "Learn the theory behind your art", "Theory helps you understand and improve what you perform.", SWAYAM,
         "Learn one new raga, rhythm or dance piece each month, and write what makes it special."),
    step(2, 1, "Perform in front of people", "Stage confidence grows only by performing.", SANGEET,
         "Perform at least once a month: in college, a temple, a function or online."),
    step(2, 2, "Learn from senior artists", "Masters teach details that books cannot.", SANGEET,
         "Attend one concert or workshop each month, and note one thing to try yourself."),
    step(3, 1, "Record and share your work", "Recordings help you improve and let people find you.", SWAYAM,
         "Record one performance, watch it back, and list three things to improve."),
    step(3, 2, "Start teaching beginners", "Teaching deepens your own skill and can become a career.", NCS,
         "Teach one beginner for a few weeks, and plan each class."),
    step(4, 1, "Learn about grants, competitions and auditions", "Many artists grow through competitions and government support.", SANGEET,
         "Read the Sangeet Natak Akademi website, and note one programme or award you could aim for."),
    step(4, 2, "Plan your next step", "Artists perform, teach, or study further, often all three.", NCS,
         "Write a one-page plan for the next two years: performing, teaching and study."),
])

from scripts.engineering_links import COURSE_ROADMAPS  # noqa: E402


from scripts.courses_links import COURSE_ROADMAPS as _DEGREE_ROADMAPS  # noqa: E402


def link_courses(goals: list[dict]) -> list[dict]:
    """Adds the newer courses to the paths they lead to."""
    for goal in goals:
        for course, roadmaps in {**COURSE_ROADMAPS, **_DEGREE_ROADMAPS}.items():
            if goal["slug"] in roadmaps and course not in goal["courses"]:
                goal["courses"].append(course)
    return goals
