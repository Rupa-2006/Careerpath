"""
How a shared career fits each course. slug: (years to show on the path, or None to keep the path's years, note)
Years are only set where the course length is on the site. This is general guidance.
"""

COURSE_PATHS = {
    "btech-cse": (None, "Your degree covers computer science in depth, so build strong programming and systems basics first."),
    "btech-it": (None, "Your degree leans towards software and networks. Use your projects to show real applications."),
    "btech-cse-ds": (None, "Your degree focuses on data, so do extra work in statistics and databases."),
    "btech-ai-ds": (None, "Your degree mixes AI and data. Decide early which side you enjoy, and build projects there."),
    "btech-cse-cyber": (None, "Your degree focuses on security, so start networks and operating systems early."),
    "bca": (3, "BCA is a 3-year course, so your path is shorter. Start projects early, and think about MCA if you want to go further."),
    "bsc-cs": (3, "This is a 3-year science degree, so your path is shorter. Add practical projects, because the course can be more theory-based."),
    "bcom": (3, "B.Com gives you a broad base in about 3 years. You can add CA, CMA or CS alongside or after it."),
    "ca": (None, "CA goes by levels, not college years. Treat each year here as one stage, and check ICAI for the current rules."),
    "cma": (None, "CMA goes by levels, not college years. Treat each year here as one stage, and check ICMAI for the current rules."),
    "bams": (None, "Your path follows Ayurveda. Learn its classical basics alongside modern health knowledge."),
    "bhms": (None, "Your path follows Homeopathy. Learn its principles alongside modern health knowledge."),
    "bums": (None, "Your path follows Unani medicine. Learn its principles alongside modern health knowledge."),
    "bnys": (None, "Your path follows Naturopathy and Yoga. Practise yoga and lifestyle care alongside your theory."),
    "bsc-mlt": (3, "Your course focuses on laboratory work, so give extra time to lab skills and accuracy."),
    "bsc-allied": (4, "Your course has one specialty, such as dialysis or radiology. Focus on the equipment and skills for that specialty."),
    "bvsc": (None, "Your path focuses on animal health, so spend time with farm animals and clinics."),
    "bfsc": (None, "Your path focuses on fish and water life, so spend time at fish farms and hatcheries."),
    "b-des": (4, "B.Des focuses on solving problems through design. Build a portfolio of real projects."),
    "bfa": (4, "BFA focuses on art practice. Build a portfolio in your specialty, such as painting or animation."),
    "bsc-agri": (None, "Your degree covers crops, soil and farm science, so spend time in the field."),
    "bsc-horti": (None, "Your degree focuses on fruit, vegetables and flowers, so learn nursery and garden work."),
    "bpharm": (None, "B.Pharm focuses on medicines and how they are made. Learn lab and quality work well."),
    "pharm-d": (None, "Pharm.D focuses on patient care. Spend extra time in hospital work."),
}


from scripts.engineering_links import COURSE_NOTES  # noqa: E402

COURSE_PATHS.update(COURSE_NOTES)
