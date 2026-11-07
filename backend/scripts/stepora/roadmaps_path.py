"""
More career roadmaps, added on 6 November 2026. The site is English only, so Telugu text is left empty.
This is general guidance written for review. It sets no admission rules, fees or salaries.
Same step format as roadmaps.py.
"""
from .roadmaps import INTERNSHALA, NCS, NPTEL, SWAYAM

DCI = "https://dciindia.gov.in/"
WHO = "https://www.who.int/health-topics/"
NCHM = "https://nchm.gov.in/"


def step(year, position, title, why, resources, build):
    return (year, 1, position, title, "", why, "", resources, build, "")


def goal(slug, name, description, courses, steps):
    return {
        "slug": slug, "name_en": name, "name_te": "", "description_en": description, "description_te": "",
        "courses": courses, "uses_semesters": False, "steps": steps,
    }


PATH_GOALS = [
    goal("civil-engineer", "Civil Engineer", "How to grow from basic engineering subjects to working on real structures.", ["btech-civil"], [
        step(1, 1, "Build your maths and mechanics base", "Almost every civil subject depends on maths and on how forces act on structures.", NPTEL,
             "Solve one mechanics problem each day, and keep your solutions in a notebook."),
        step(2, 1, "Learn surveying and building materials", "Every project starts with measuring land and choosing the right materials.", NPTEL,
             "Visit a building site near you, and list the materials you see and why they were used."),
        step(3, 1, "Learn structures and drawing software", "Engineers explain their designs through drawings, so this is a daily skill.", SWAYAM,
             "Draw the plan of one small house using drawing software."),
        step(3, 2, "Get real site experience", "Site work teaches what classrooms can't, like planning, safety and working with people.", INTERNSHALA,
             "Do one site internship and keep a short daily diary of what you learned."),
        step(4, 1, "Choose an area and finish a strong project", "A focused project shows employers what you can do.", NPTEL,
             "Pick one area, such as structures, transport or water, and finish a final-year project in it."),
        step(4, 2, "Prepare for jobs or higher study", "Decide early between jobs, government exams and further study, because each needs its own preparation.", NCS,
             "Make a one-page resume, and write down your next three steps."),
    ]),
    goal("electrical-engineer", "Electrical Engineer", "How to grow from circuits to power systems and real electrical work.", ["btech-eee"], [
        step(1, 1, "Build your maths and circuits base", "Circuits and maths are the language of every electrical subject.", NPTEL,
             "Solve circuit problems each week, and check your answers using a free circuit simulator."),
        step(2, 1, "Learn electrical machines and measurements", "Motors, generators and transformers are at the heart of this field.", NPTEL,
             "In your lab, record how a machine behaves when its load changes."),
        step(2, 2, "Learn basic programming", "Modern electrical systems are controlled by software.", SWAYAM,
             "Write a small program that reads numbers and draws a simple graph."),
        step(3, 1, "Learn power systems and control", "These subjects explain how electricity reaches homes and stays stable.", NPTEL,
             "Trace how electricity reaches your home, and draw it as a simple diagram."),
        step(3, 2, "Get real industry experience", "Seeing real equipment and safety rules at work builds confidence.", INTERNSHALA,
             "Do one internship, and note the safety rules that were followed."),
        step(4, 1, "Finish a project and prepare for jobs", "A working project shows what you can do, and early preparation gives you more choices.", NCS,
             "Finish one working project, and make a one-page resume."),
    ]),
    goal("dentist", "Dentist (BDS)", "What to focus on through the BDS course and internship.", ["bds"], [
        step(1, 1, "Build strong study habits", "Early subjects about the body and teeth support everything that comes later.", SWAYAM,
             "Make a weekly revision timetable and follow it for one month."),
        step(2, 1, "Practise your hand skills", "Dentistry needs very steady, careful hands, and these improve with regular practice.", DCI,
             "Use your lab practice time fully, and ask seniors to point out your mistakes."),
        step(3, 1, "Connect subjects to real patients", "Understanding disease and medicines helps you treat patients safely.", WHO,
             "For one common mouth problem, write how it starts and how it can be prevented."),
        step(4, 1, "Learn to talk with patients", "Many patients are afraid. Clear, kind talk builds trust.", DCI,
             "In your clinical postings, practise explaining treatment in simple words."),
        step(5, 1, "Make the most of your internship", "The internship is where you learn to work as a dentist.", DCI,
             "Keep a logbook of what you learn, and note which areas you enjoy."),
        step(5, 2, "Plan your next step", "You need to know the registration rules, then choose between a job, your own practice or further study.", DCI,
             "Check the current registration steps on the official website."),
    ]),
    goal("physiotherapist", "Physiotherapist (BPT)", "How to grow from learning the body to helping patients recover.", ["bpt"], [
        step(1, 1, "Learn how the body moves", "Everything in physiotherapy depends on knowing muscles, bones and joints.", SWAYAM,
             "Choose one joint, and explain how it moves using a drawing."),
        step(2, 1, "Learn exercise and treatment methods", "These are the main tools you will use with patients.", WHO,
             "Practise each method under your teacher's guidance, and note when it should not be used."),
        step(3, 1, "Start working with real patients", "Each patient is different, so you must learn to listen and observe.", WHO,
             "In your clinical postings, write how one patient improved over time."),
        step(4, 1, "Explore different areas", "Physiotherapy covers sports, older people, children and recovery after surgery.", NCS,
             "Spend time in different departments, and note which one suits you."),
        step(4, 2, "Make the most of your internship", "The internship turns what you learned into real skill.", NCS,
             "Keep a logbook, and make a one-page resume before it ends."),
    ]),
    goal("designer", "Designer (B.Des or BFA)", "How to build your skills and portfolio as a designer or artist.", ["b-des", "bfa"], [
        step(1, 1, "Draw and observe every day", "Regular drawing trains your eye, and it is the base of all design and art.", SWAYAM,
             "Keep a sketchbook, and fill one page every day."),
        step(1, 2, "Learn basic design ideas", "Colour, shape and layout decide whether a design works.", SWAYAM,
             "Redesign one poster you see around you, and explain your changes."),
        step(2, 1, "Learn your main digital tools", "Most design work today is done on a computer.", SWAYAM,
             "Finish one small digital project from start to end."),
        step(3, 1, "Solve real problems for real people", "Good design begins by understanding the people who will use it.", INTERNSHALA,
             "Talk to three people about a problem, then design something that helps them."),
        step(3, 2, "Start your portfolio", "Employers mostly judge designers by their work, not their marks.", INTERNSHALA,
             "Collect your best five projects, and explain how you made each one."),
        step(4, 1, "Get experience and choose your area", "Internships and freelance work show you what you enjoy.", NCS,
             "Do one internship, and improve your portfolio using what you learned."),
    ]),
    goal("hotel-manager", "Hotel and Hospitality Manager", "How to grow from basic hotel skills to managing guests and teams.", ["bsc-hha"], [
        step(1, 1, "Learn the four main hotel areas", "Food production, food service, front office and housekeeping are the base of this work.", NCHM,
             "In your labs, note what each team does and how they depend on each other."),
        step(1, 2, "Improve how you speak with guests", "This is a people job, so clear and polite speech matters every day.", SWAYAM,
             "Practise greeting guests and handling one complaint with a friend."),
        step(2, 1, "Do your industrial training well", "Real hotel work shows you the speed and discipline this job needs.", NCHM,
             "Keep a short diary of what you learn in each department."),
        step(2, 2, "Learn food safety and costs", "A hotel must keep guests safe and also make money.", NCHM,
             "Work out the cost of one simple dish, and how it could be priced."),
        step(3, 1, "Choose your area", "Hotels, flight kitchens, events and tourism each need different strengths.", NCS,
             "Talk to two seniors working in different areas, and write what you learned."),
        step(3, 2, "Prepare for your first job", "Hotels often hire through campus interviews, so be ready early.", NCS,
             "Make a one-page resume, and practise answering common interview questions."),
    ]),
]
