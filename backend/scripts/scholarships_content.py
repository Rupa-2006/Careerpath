"""
Scholarships and education loans. Everything loads as 'pending_verification', so an admin must check each one.

Rules come only from official pages, read on 5 to 7 November 2026. audience is all, girls or disability. kind is scholarship, loan or portal.
state is AP, TS, or None for all of India.
"""

# slug, name, run by, kind, audience, state, who can apply, what you get, how to apply, apply url, source
SCHOLARSHIPS = [
    ("pm-usp-csss", "PM-USP Central Sector Scholarship for College and University Students",
     "Department of Higher Education, Ministry of Education", "scholarship", "all", None,
     "You must be above the 80th percentile of those who passed in your stream and board in Class 12, and study a regular "
     "degree course. Family income must be up to ₹4.5 lakh a year. You can't apply if you are in a diploma or distance course, "
     "took a drop after Class 12, or get another scholarship or fee reimbursement.",
     "₹12,000 a year for the first three years of a degree. B.Tech students get ₹20,000 in the 4th year. "
     "To keep it each year, you need at least 50% marks and 75% attendance.",
     "Apply on the National Scholarship Portal.", "https://scholarships.gov.in/", "pm-usp"),
    ("aicte-pragati-degree", "AICTE Pragati Scholarship for Girl Students (Technical Degree)",
     "All India Council for Technical Education", "scholarship", "girls", None,
     "Girls admitted to the first year of a degree course at an AICTE-approved institution, or to the second year through "
     "lateral entry. Up to two girls per family. Family income must be up to ₹8 lakh a year. These rules are from the "
     "2020-21 guidelines, which the portal still links to, so check them before applying.",
     "₹50,000 a year, for up to 4 years. 5,000 scholarships a year are shared across states. A separate scheme exists for diploma students.",
     "Apply on the National Scholarship Portal.", "https://scholarships.gov.in/", "pragati"),
    ("aicte-saksham-degree", "AICTE Saksham Scholarship for Specially-Abled Students (Technical Degree)",
     "All India Council for Technical Education", "scholarship", "disability", None,
     "Students with a disability of at least 40%, admitted to the first year of a degree course at an AICTE-approved "
     "institution, or to the second year through lateral entry. Family income must be up to ₹8 lakh a year. These rules are "
     "from the 2020-21 guidelines, which the portal still links to, so check them before applying.",
     "₹50,000 a year, for up to 4 years. A separate scheme exists for diploma students.",
     "Apply on the National Scholarship Portal.", "https://scholarships.gov.in/", "saksham"),
    ("national-scholarship-portal", "National Scholarship Portal (all central schemes)",
     "Government of India", "portal", "all", None,
     "It depends on each scheme. The portal has an eligibility checker.",
     "One place to find and apply for central schemes. You may apply for one merit-based scheme and one or more welfare-based schemes.",
     "First get your 14-digit One Time Registration (OTR) number, then apply. The portal opened for 2026-27 on 1 June 2026.",
     "https://scholarships.gov.in/", "nsp"),
    ("telangana-epass", "Telangana ePASS Post Matric Scholarship", "Social Welfare Department, Government of Telangana", "scholarship", "all", "TS",
     "Yearly family income limits: SC up to ₹2.5 lakh, ST up to ₹2 lakh, BC, EBC and Minority up to ₹1.5 lakh in rural areas or ₹2 lakh in urban areas, "
     "and Disabled Welfare students up to ₹1 lakh. To renew, you need 75% attendance each quarter and promotion to the next year. Not eligible: part-time, "
     "online and correspondence courses, and Management Quota, Sponsored and Spot Admission seats. EBC students in Intermediate are not eligible, except "
     "those selected under the Corporate College Admissions Scheme.",
     "Tuition fee reimbursement, paid directly to the college, and a monthly maintenance amount paid to the student. The portal's maintenance table comes "
     "from a 2017 order: for SC, ST, BC, Minority and Disabled students it is ₹1,500 for students in college-attached hostels in professional courses and ₹1,000 in degree courses, "
     "and ₹650 for day scholars in professional courses and ₹500 in degree courses. Check the current rates on the portal.",
     "Register online, and upload your caste, income and Aadhaar details, marks memo, bonafide certificate, ration card and bank pass book. "
     "Professional course students also need their CET allotment order.",
     "https://telanganaepass.cgg.gov.in/", "tg-epass"),
    ("ap-jnanabhumi", "AP Post Matric Scholarship (Jnanabhumi: RTF and MTF)", "Social Welfare Department, Government of Andhra Pradesh", "scholarship", "all", "AP",
     "For SC, ST, BC, EBC, Kapu, Minority and Differently Abled students in Polytechnic, ITI, and Degree and above courses, at Government, Aided or Private colleges "
     "affiliated to State Universities or Boards. You need 75% attendance. Family income must be up to ₹2.5 lakh a year. The family must hold less than 10 acres of wet "
     "land or 25 acres of dry land, or 25 acres in total. In urban areas, it must own less than 1,500 sq ft of built-up area. No family member can be a government "
     "employee or pensioner (sanitary workers are allowed), pay income tax, or own a four-wheeler (taxis, tractors and autos are allowed). Not eligible: Private or "
     "Deemed Universities, correspondence or distance courses, and Management or Spot Quota seats. The page shows no year, so confirm these rules for the current year.",
     "RTF: full fee reimbursement, paid to the college. MTF: for food and hostel costs each year, ₹10,000 for ITI, ₹15,000 for Polytechnic and ₹20,000 for Degree and "
     "above courses. MTF goes to the mother's account, or to the natural guardian if she has died or is absent.",
     "Collect the Jnanabhumi Scholarship Application Form from your college, fill it in and give it to the Principal, who submits it online. Then visit a Mee Seva Centre "
     "with your application ID and Aadhaar number to check and confirm it with your biometric.",
     "https://jnanabhumi.ap.gov.in/", "ap-jnanabhumi"),
    ("pm-vidyalaxmi", "PM-Vidyalaxmi education loans",
     "Department of Financial Services, Department of Higher Education and Indian Banks' Association", "loan", "all", None,
     "Students studying in India or abroad. For the government's credit guarantee, the institute must be an eligible Quality "
     "Higher Education Institution under the NIRF ranking.",
     "Loans up to ₹7.5 lakh can get a 75% credit guarantee. If family income is up to ₹8 lakh a year, the scheme gives 3% interest "
     "help on loans up to ₹10 lakh. If it is up to ₹4.5 lakh, the scheme gives full interest help. A loan must be paid back.",
     "Apply through the student login on the official portal.", "https://pmvidyalaxmi.co.in/", "pmvl"),
]
