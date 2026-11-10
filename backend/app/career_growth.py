"""
How people commonly grow in each career, and what to have ready for a first job.
General guidance for students. Titles differ between employers, and nothing here is a job guarantee.

career: (first role, after experience, senior role, what to have ready)
"""

COMPUTER_READY = ["Two or three projects you built yourself", "Your code on GitHub", "A one-page resume", "Practice explaining your projects"]
HEALTH_READY = ["Completed internship or clinical training", "Registration, if your field requires it", "A one-page resume", "Practice talking with patients"]
ENGINEERING_READY = ["One strong final-year project", "An internship or site or plant visit", "A one-page resume", "Practice explaining your core subjects"]

CAREER_GROWTH = {
    "web-developer": ("Junior Developer", "Software Developer", "Senior Developer or Tech Lead", COMPUTER_READY),
    "ai-engineer": ("Junior ML Engineer", "Machine Learning Engineer", "Senior AI Engineer or AI Lead", COMPUTER_READY),
    "cyber-security-analyst": ("SOC Analyst", "Security Analyst or Penetration Tester", "Security Architect or Security Manager", ["Practice labs you have finished", "A home lab or security project", "A one-page resume", "Clear notes on what you tested and learned"]),
    "data-analyst": ("Junior Data Analyst", "Data Analyst or Data Scientist", "Senior Data Scientist or Analytics Manager", ["Two or three data projects", "Charts you can explain", "A one-page resume", "Practice with SQL and spreadsheets"]),
    "embedded-engineer": ("Graduate Engineer Trainee", "Embedded Engineer", "Senior Engineer or Systems Architect", ENGINEERING_READY),
    "electrical-engineer": ("Graduate Engineer Trainee", "Electrical Engineer", "Senior Engineer or Project Manager", ENGINEERING_READY),
    "mechanical-engineer": ("Graduate Engineer Trainee", "Design or Production Engineer", "Senior Engineer or Plant Manager", ENGINEERING_READY),
    "chemical-engineer": ("Graduate Engineer Trainee or Process Trainee", "Process or Plant Engineer", "Senior Process Engineer or Plant Manager", ENGINEERING_READY),
    "civil-engineer": ("Junior Site Engineer", "Site or Structural Engineer", "Project Manager or Senior Consultant", ENGINEERING_READY),
    "architect": ("Junior Architect", "Project Architect", "Senior Architect or Practice Owner", ["A strong portfolio", "Practical office training", "Your registration details, once ready", "Practice explaining your designs"]),
    "doctor": ("Junior Resident or Medical Officer", "Specialist, after postgraduate study", "Senior Consultant or Head of Department", HEALTH_READY),
    "nurse": ("Staff Nurse", "Senior Nurse or Ward In-charge", "Nursing Superintendent or Nurse Educator", HEALTH_READY),
    "dentist": ("Associate Dentist", "Dental Surgeon", "Specialist or Clinic Owner", HEALTH_READY),
    "pharmacist": ("Pharmacist", "Senior Pharmacist or Quality Officer", "Pharmacy Manager or Quality Head", ["Completed practical training", "Registration, if your role requires it", "A one-page resume", "Practice explaining safe medicine use"]),
    "physiotherapist": ("Junior Physiotherapist", "Physiotherapist", "Senior Physiotherapist or Clinic Owner", HEALTH_READY),
    "health-technologist": ("Junior Technologist", "Senior Technologist", "Department Lead or Lab Manager", ["Completed hospital training", "A list of equipment you can use", "A one-page resume", "Good safety habits you can explain"]),
    "traditional-medicine-doctor": ("Junior Doctor", "Experienced Practitioner", "Senior Consultant or Clinic Owner", HEALTH_READY),
    "accounts-finance": ("Accounts Assistant or Article Assistant", "Accountant or Finance Executive", "Finance Manager or Partner", ["Practice with spreadsheets", "Basic accounting and tax knowledge", "A one-page resume", "Any articleship or internship work"]),
    "business-manager": ("Management Trainee", "Team Lead or Assistant Manager", "Manager or Business Head", ["An internship you can talk about", "A project with real results", "A one-page resume", "Practice speaking clearly"]),
    "company-secretary": ("CS Trainee", "Company Secretary", "Senior Compliance Head or Practising CS", ["Your practical training", "Knowledge of company law basics", "A one-page resume", "Clear writing samples"]),
    "hotel-manager": ("Trainee", "Supervisor or Duty Manager", "General Manager", ["Your industrial training", "Good guest communication", "A one-page resume", "A smart, professional manner"]),
    "advocate": ("Junior Advocate or Legal Associate", "Independent Advocate", "Senior Advocate or Legal Head", ["Internships with lawyers or firms", "Enrolment details, once ready", "A one-page resume", "Writing samples of legal drafts"]),
    "civil-services": ("Entry post through your exam", "Mid-level officer", "Senior officer", ["A steady study routine", "Good current affairs knowledge", "Practice writing answers", "A backup career plan"]),
    "government-exams": ("Entry post through your exam", "Senior Assistant", "Section Officer or similar", ["A steady study routine", "Regular mock tests", "Typing and computer skills", "A backup career plan"]),
    "defence-officer": ("Commissioned Officer", "Senior Officer", "Commanding Officer", ["Good physical fitness", "Practice for group tasks and interviews", "A strong record of discipline", "A backup career plan"]),
    "social-worker": ("Field Worker", "Programme Officer", "Programme Manager or NGO Head", ["Field work or volunteering", "Stories of who you helped", "A one-page resume", "Good listening skills"]),
    "researcher": ("Research Assistant", "Research Scientist", "Principal Scientist or Professor", ["A research project or thesis", "A clear summary of your work", "A one-page CV", "Teachers who can recommend you"]),
    "agriculture-officer": ("Field Officer or Trainee", "Agriculture Officer", "Senior Manager or Deputy Director", ["Field experience", "Knowledge of local crops", "A one-page resume", "Practice talking with farmers"]),
    "animal-and-fisheries": ("Junior Veterinary or Fisheries Officer", "Veterinary Doctor or Fisheries Officer", "Senior Officer or Farm Owner", ["Field or clinic experience", "Registration, if your role requires it", "A one-page resume", "Practice talking with farmers"]),
    "designer": ("Junior Designer", "Designer", "Senior Designer or Design Lead", ["A strong portfolio", "Three projects you can explain", "A one-page resume", "Practice taking feedback"]),
    "pilot": ("First Officer", "Senior First Officer", "Captain or Instructor", ["Your licences and medical in order", "Your logbook", "A one-page resume", "A backup career plan"]),
    "physical-education-teacher": ("PE Teacher or Assistant Coach", "Senior PE Teacher or Coach", "Head of Sports", ["Your teaching practice", "Sports you can coach", "First-aid knowledge", "A one-page resume"]),
    "vocational-professional": ("Trainee or Technician", "Supervisor", "Manager or Business Owner", ["Proof of your practical skills", "Internship experience", "A one-page resume", "Certificates in your trade"]),
}
