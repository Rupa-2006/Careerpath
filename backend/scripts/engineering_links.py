"""Paths and course notes for the B.Tech branches in engineering_more.py. Kept separate so nothing imports in a circle."""

# Which career path each new branch leads to (added to those roadmaps' course lists)
COURSE_ROADMAPS = {
    "btech-ai": ["ai-engineer", "data-analyst"],
    "btech-csbs": ["web-developer", "data-analyst"],
    "btech-cs-design": ["web-developer", "designer"],
    "btech-cse-iot": ["embedded-engineer"],
    "btech-eie": ["embedded-engineer", "electrical-engineer"],
    "btech-robotics": ["embedded-engineer", "mechanical-engineer", "ai-engineer"],
    "btech-automobile": ["mechanical-engineer"],
    "btech-aeronautical": ["mechanical-engineer"],
    "btech-chemical": ["chemical-engineer"],
}

# How the shared path fits each branch (shown as "For your course")
COURSE_NOTES = {
    "btech-ai": (None, "Your degree is all about AI, so build strong maths and Python early, then do real AI projects."),
    "btech-csbs": (None, "Your degree mixes computing and business. Build software projects that solve a real business problem."),
    "btech-cs-design": (None, "Your degree mixes code and design. Keep a portfolio with both apps you built and screens you designed."),
    "btech-cse-iot": (None, "Your degree connects devices to the internet. Do hands-on projects with sensors and small boards."),
    "btech-eie": (None, "Your degree focuses on measuring and controlling machines. Give extra time to sensors and control systems."),
    "btech-robotics": (None, "Your degree mixes mechanics, electronics and code. Build small robots, and join a robotics club or contest."),
    "btech-automobile": (None, "Your degree focuses on vehicles. Learn engines and electric vehicles, and visit service centres and factories."),
    "btech-aeronautical": (None, "Your degree focuses on aircraft. Learn aerodynamics and materials well, and look for training at aviation companies."),
    "btech-chemical": (None, "Your degree is about chemical plants and processes. Strong chemistry and plant safety matter most."),
}

COURSE_ROADMAPS.update({
    "btech-mining": ["mining-metallurgy-engineer"],
    "btech-metallurgy": ["mining-metallurgy-engineer"],
    "btech-textile": ["mechanical-engineer", "chemical-engineer"],
    "btech-petroleum": ["chemical-engineer"],
    "btech-biotech": ["researcher"],
    "btech-biomedical": ["embedded-engineer", "health-technologist"],
    "btech-food-tech": ["chemical-engineer", "agriculture-officer"],
    "btech-dairy": ["agriculture-officer", "chemical-engineer"],
    "btech-pharma-eng": ["chemical-engineer", "pharmacist"],
    "btech-agri-eng": ["agriculture-officer", "mechanical-engineer"],
})

COURSE_NOTES.update({
    "btech-mining": (None, "Your degree is about mines. Safety rules and field visits matter as much as theory."),
    "btech-metallurgy": (None, "Your degree is about metals. Learn lab testing well, and visit a steel or metal plant."),
    "btech-textile": (None, "Your degree is about fibres and fabrics. Visit a mill, and learn both machines and textile chemistry."),
    "btech-petroleum": (None, "Your degree is about oil and gas. Strong chemistry, geology and safety matter most."),
    "btech-biotech": (None, "Your degree mixes biology and engineering. Do lab projects, and think early about research or industry."),
    "btech-biomedical": (None, "Your degree is about medical devices. Learn electronics well, and spend time in a hospital's equipment section."),
    "btech-food-tech": (None, "Your degree is about food processing. Learn food safety rules and visit a food factory."),
    "btech-dairy": (None, "Your degree is about milk and dairy products. Visit a dairy plant, and learn hygiene and quality well."),
    "btech-pharma-eng": (None, "Your degree is about medicine factories. Learn quality rules and how plants are run."),
    "btech-agri-eng": (None, "Your degree is about farm machines and water. Spend time on farms and with irrigation projects."),
})
