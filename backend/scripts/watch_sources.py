"""
Checks official pages for changes:  python -m scripts.watch_sources
The first run saves each page. Later runs alert an admin when a page changes. It never edits student content.
"""
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import SourceWatch
from app.watch import check_all

# name, url, what it affects
WATCHES = [
    ("OWASP Top 10", "https://top10.owasp.org/2025/", "Web Developer and Cyber Security roadmaps"),
    ("NIST Post-Quantum Cryptography", "https://csrc.nist.gov/projects/post-quantum-cryptography", "Cyber Security roadmap"),
    ("NIST AI Risk Management Framework", "https://www.nist.gov/itl/ai-risk-management-framework", "Data Analyst roadmap"),
    ("India Semiconductor Mission", "https://ism.gov.in/", "Embedded and Electrical roadmaps"),
    ("NTA engineering exams", "https://nta.ac.in/Engineeringexam", "B.Tech rules and JEE Main"),
    ("JEE Main", "https://jeemain.nta.nic.in/", "JEE Main dates"),
    ("JEE Advanced", "https://jeeadv.ac.in/", "JEE Advanced rules"),
    ("NEET UG", "https://neet.nta.nic.in/", "NEET dates and medical rules"),
    ("CUET UG", "https://cuet.nta.nic.in/", "CUET rules"),
    ("AP entrance exams", "https://cets.apsche.ap.gov.in/APSCHE/APSCHEHome.aspx", "AP EAPCET, LAWCET, ECET and PECET dates"),
    ("TG EAPCET", "https://eapcet.tgche.ac.in/", "TG EAPCET dates and rules"),
    ("TG LAWCET", "https://lawcet.tgche.ac.in/", "TG LAWCET dates and rules"),
    ("TG LAWCET eligibility", "https://lawcet.tgche.ac.in/UI/Eligibility.aspx", "BA LLB rule for Telangana"),
    ("TG ECET", "https://ecet.tgche.ac.in/", "TG ECET rules"),
    ("TG PECET", "https://pecet.tgche.ac.in/", "TG PECET and D.P.Ed rules"),
    ("DOST", "https://dost.cgg.gov.in/", "Telangana degree admissions"),
    ("DOST course list", "https://dost.cgg.gov.in/viewUGCourses.htm", "Full course list for Telangana"),
    ("KNRUHS admissions", "https://www.knruhs.telangana.gov.in/admission-notification/", "Telangana health courses"),
    ("PM E-DRIVE", "https://pmedrive.heavyindustries.gov.in/about-us", "Mechanical and Electrical: what is changing"),
    ("FSSAI Hygiene Rating", "https://hygiene.fssai.gov.in/about.php", "Hotel Manager: what is changing"),
    ("Mission Karmayogi", "https://dopt.gov.in/schemes/national-programme-civil-services-and-capacity-building-npcscb-mission-karmayogi", "Government jobs: what is changing"),
    ("CLAT eligibility", "https://consortiumofnlus.ac.in/clat-2027/ug-eligibility.html", "BA LLB rule for CLAT"),
    ("National Scholarship Portal", "https://scholarships.gov.in/", "Central scholarships"),
    ("Telangana ePASS", "https://telanganaepass.cgg.gov.in/", "Telangana scholarships"),
    ("PM-Vidyalaxmi", "https://pmvidyalaxmi.co.in/", "Education loans"),
]


def load_watches(db) -> None:
    for name, url, affects in WATCHES:
        watch = db.scalar(select(SourceWatch).where(SourceWatch.url == url))
        if watch is None:
            watch = SourceWatch(url=url)
            db.add(watch)
        watch.name, watch.affects = name, affects
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        load_watches(db)
        counts = check_all(db)
    print("Source watch finished:", ", ".join(f"{count} {name}" for name, count in sorted(counts.items())))


if __name__ == "__main__":
    main()
