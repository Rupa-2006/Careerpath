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
