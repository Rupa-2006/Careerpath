"""
What opens up after each roadmap. Links go to places that list real openings, because we never invent vacancies.
This is general career guidance. It gives no salaries or job guarantees. Rules for each exam are on its official site.

roadmap: (job roles, higher study, government or public routes, working for yourself)
"""
NCS = "https://www.ncs.gov.in/"
INTERNSHALA = "https://internshala.com/"
UPSC = "https://upsc.gov.in/"
SSC = "https://ssc.gov.in/"
NPTEL = "https://nptel.ac.in/"

TECH_GOVT = "Public sector companies and government technical posts. Watch official notices for each opening."
ENGG_STUDY = "M.Tech or MS. Many M.Tech seats in India use the GATE exam."
COMPUTER_STUDY = "M.Tech or MS after a B.Tech, or MCA or M.Sc after BCA or B.Sc. Many M.Tech seats in India use the GATE exam."
HEALTH_GOVT = "Government hospitals and health departments. Watch official state and central notices."

OPPORTUNITIES = {
    "web-developer": ("Frontend Developer, Backend Developer, Full Stack Developer", COMPUTER_STUDY, TECH_GOVT, "Freelance websites and apps, or start a small software business."),
    "cyber-security-analyst": ("Security Analyst, SOC Analyst, Penetration Tester", COMPUTER_STUDY + " You can also add security certifications.", TECH_GOVT, "Freelance security testing, once you have enough experience and written permission from clients."),
    "data-analyst": ("Data Analyst, Business Analyst, Junior Data Scientist", "Master's in data science, statistics or computer science.", TECH_GOVT, "Freelance data and reporting work."),
    "ai-engineer": ("AI Engineer, Machine Learning Engineer, Data Scientist", "M.Tech or MS in AI or data science. Many M.Tech seats in India use the GATE exam.", TECH_GOVT, "Freelance AI and data projects, or start a small software business."),
    "business-manager": ("Management Trainee, Marketing Executive, HR Executive, Operations Executive", "MBA, or a postgraduate degree in management.", "Bank and public sector exams. Watch official notices.", "Start a small business."),
    "embedded-engineer": ("Embedded Engineer, Firmware Engineer, IoT Engineer", ENGG_STUDY, TECH_GOVT, "Build and sell small hardware products."),
    "pharmacist": ("Hospital Pharmacist, Community Pharmacist, Quality Control Analyst", "M.Pharm or Pharm.D, depending on your degree.", HEALTH_GOVT, "Run a pharmacy, after meeting registration and licence rules."),
    "accounts-finance": ("Accountant, Tax Assistant, Audit Assistant, Finance Executive", "M.Com, MBA, or professional courses such as CA, CMA and CS.", "Bank exams and SSC exams. Watch official notices.", "Offer bookkeeping and tax help, within what your qualification allows."),
    "civil-services": ("Civil Servant through UPSC or your State Public Service Commission", "A master's degree in your subject, if you want a backup path.", "UPSC and State PSC exams. Check age and attempt limits in each notice.", "Your degree and preparation also help in policy, teaching and NGO work."),
    "doctor": ("Medical Officer, Junior Resident, Hospital Doctor", "MD, MS or diploma courses. Admission uses NEET PG.", HEALTH_GOVT, "Private practice, after meeting registration rules."),
    "nurse": ("Staff Nurse, Community Health Nurse, Nursing Tutor", "M.Sc Nursing or a specialised nursing course.", HEALTH_GOVT, "Home care services, after meeting registration rules."),
    "agriculture-officer": ("Agriculture Officer, Farm Manager, Seed or Fertiliser Company Executive", "M.Sc in an agriculture subject, then research if you enjoy it.", "State agriculture department posts and agricultural banking posts. Watch official notices.", "Start an agri-business, nursery or organic farming unit."),
    "mechanical-engineer": ("Design Engineer, Production Engineer, Maintenance Engineer", ENGG_STUDY, TECH_GOVT, "Start a small workshop or design service."),
    "teacher": ("School Teacher, Tuition or Online Teacher, Teaching Assistant", "M.Sc or M.A in your subject, then M.Ed if you want to teach teachers.", "Government school teacher posts, after the required teacher tests. Watch official notices.", "Start a tuition centre or teach online."),
    "lab-analyst": ("Lab Assistant, Quality Control Analyst, Testing Lab Technician", "M.Sc in your subject.", "Government testing labs and public sector companies. Watch official notices.", "Later, a small testing or quality consulting service, after meeting local rules."),
    "performing-artist": ("Performing Artist, Accompanist, Music or Dance Teacher", "MPA or a master's degree in music or dance.", "Cultural departments and government school arts posts. Watch official notices.", "Start your own music or dance classes."),
    "mining-metallurgy-engineer": ("Mining Engineer, Metallurgical Engineer, Quality and Safety Engineer", ENGG_STUDY, TECH_GOVT, "Work as a consultant for testing or safety, after meeting local rules."),
    "chemical-engineer": ("Process Engineer, Plant Engineer, Quality and Safety Engineer", ENGG_STUDY, TECH_GOVT, "Start a small testing or consulting service, after meeting local rules."),
    "advocate": ("Advocate, Legal Associate, Company Legal Executive", "LL.M, in a subject such as corporate or criminal law.", "Judicial service exams and government law officer posts. Watch official notices.", "Independent practice, after enrolling with a State Bar Council."),
    "civil-engineer": ("Site Engineer, Structural Engineer, Quantity Surveyor", ENGG_STUDY, TECH_GOVT, "Work as a contractor or consultant, after meeting local licence rules."),
    "electrical-engineer": ("Electrical Engineer, Power Systems Engineer, Maintenance Engineer", ENGG_STUDY, "Power companies and public sector companies. Watch official notices.", "Work as an electrical contractor, after meeting licence rules."),
    "dentist": ("Dental Surgeon, Hospital Dentist, Associate Dentist", "MDS, in a specialty you enjoy.", HEALTH_GOVT, "Open a dental clinic, after meeting registration rules."),
    "physiotherapist": ("Physiotherapist in hospitals, sports teams or rehabilitation centres", "MPT, in an area such as sports or neurology.", HEALTH_GOVT, "Open a clinic or offer home visits, after meeting local rules."),
    "designer": ("UI/UX Designer, Graphic Designer, Product Designer, Animator", "M.Des or MFA.", "Design roles in public institutions. Watch official notices.", "Freelance design work, using your portfolio."),
    "hotel-manager": ("Hotel Operations Trainee, Front Office Executive, Food and Beverage Executive, Event Coordinator", "MBA or a master's degree in hospitality or tourism.", "Tourism development corporations. Watch official notices.", "Start a catering, food or event business."),
    "architect": ("Architect, Urban Designer, Interior Designer", "M.Arch or M.Plan.", "Town planning and public works departments. Watch official notices.", "Independent practice, after registering with the Council of Architecture."),
    "researcher": ("Research Assistant, Lab Scientist, Research and Development Associate", "PhD, in India or abroad.", "Government research laboratories. Watch official notices.", "Science communication, or a start-up based on your research."),
    "pilot": ("First Officer with an airline, flying instructor, charter pilot", "Further type ratings and licences, as your employer requires.", "Defence flying is a separate route, through the armed forces.", "Flying instruction, once you hold the right ratings."),
    "defence-officer": ("Commissioned Officer in the Army, Navy or Air Force", "Service courses during your career, and a degree through the Academy.", "UPSC exams such as NDA. Check each notice.", "Many officers later move to corporate, security or public roles."),
    "government-exams": ("Clerk, Data Entry Operator and other central government posts", "A degree opens more exams, such as SSC CGL and bank exams.", "SSC, railway and bank exams. Watch official notices.", "Your exam skills also help with teaching or coaching."),
    "vocational-professional": ("Supervisor or technician in your trade, such as retail, banking, dairy or healthcare", "M.Voc, or a master's in a related subject.", "Skill development and state corporation posts. Watch official notices.", "Start a small business in your trade."),
    "company-secretary": ("Company Secretary, Compliance Officer, Legal and Secretarial Executive", "LL.B or an MBA, if you want to widen your work.", "Compliance roles in public sector companies. Watch official notices.", "Practising Company Secretary, after meeting ICSI rules."),
    "health-technologist": ("Lab Technologist, Radiology Technologist, Dialysis or Operation Theatre Technologist", "A master's degree in your specialty.", HEALTH_GOVT, "Run a diagnostic lab, after meeting local rules."),
    "physical-education-teacher": ("Physical Education Teacher, School Coach, Fitness Instructor", "B.P.Ed, then M.P.Ed.", "School teacher recruitment. Watch state notices.", "Start a coaching centre or fitness classes."),
    "animal-and-fisheries": ("Veterinary Doctor, Fisheries Officer, Farm or Hatchery Manager", "M.V.Sc or M.F.Sc.", "State animal husbandry and fisheries departments. Watch official notices.", "Private practice, or a dairy, poultry or fish farm."),
    "traditional-medicine-doctor": ("Doctor in Ayurveda, Homeopathy, Unani or Naturopathy hospitals and clinics", "MD or MS in your system of medicine.", "AYUSH departments and government hospitals. Watch official notices.", "Private practice, after meeting registration rules."),
    "social-worker": ("Social Worker, Community Coordinator, NGO Programme Assistant", "MSW, the master's degree in social work.", "Welfare department and project posts. Watch official notices.", "Start or join a community organisation."),
}
