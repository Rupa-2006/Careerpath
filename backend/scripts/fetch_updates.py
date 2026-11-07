"""
Collects the latest technology headlines:  python -m scripts.fetch_updates

Only the title, link and date are stored; students read the article on the original site.
This is news, not advice, and it is never treated as an official announcement.
"""
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models import TechnologyUpdate

_HEALTH = ["doctor", "nurse", "pharmacist", "dentist", "physiotherapist", "health-technologist", "traditional-medicine-doctor"]
_FINANCE = ["accounts-finance", "company-secretary"]
_ENGINEERING = ["embedded-engineer", "electrical-engineer", "mechanical-engineer", "civil-engineer"]
FEEDS = [
    ("GitHub Blog", "https://github.blog/feed/", ["web-developer"]),
    ("web.dev", "https://web.dev/feed.xml", ["web-developer"]),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/", ["cyber-security-analyst"]),
    ("Hackaday", "https://hackaday.com/feed/", ["embedded-engineer"]),
    ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss", _ENGINEERING),
    ("Google AI", "https://blog.google/technology/ai/rss/", ["ai-engineer", "data-analyst", "web-developer"]),
    ("NIST", "https://www.nist.gov/news-events/news/rss.xml", ["cyber-security-analyst", "data-analyst", "researcher"]),
    ("WHO", "https://www.who.int/rss-feeds/news-english.xml", _HEALTH),
    ("RBI press releases", "https://www.rbi.org.in/pressreleases_rss.xml", _FINANCE),
    ("RBI notifications", "https://www.rbi.org.in/notifications_rss.xml", _FINANCE),
    ("FAO", "https://www.fao.org/feeds/fao-newsroom-rss", ["agriculture-officer", "animal-and-fisheries"]),
    ("ScienceDaily", "https://www.sciencedaily.com/rss/top/science.xml", ["researcher"]),
    ("ArchDaily", "https://www.archdaily.com/feed", ["architect", "civil-engineer"]),
    ("Dezeen", "https://www.dezeen.com/feed/", ["designer", "architect"]),
    ("United Nations", "https://www.un.org/en/rss.xml", ["social-worker", "civil-services"]),
    ("FlightGlobal", "https://www.flightglobal.com/rss", ["pilot"]),
    ("Simple Flying", "https://simpleflying.com/feed/", ["pilot"]),
    ("Bar and Bench", "https://www.barandbench.com/feed", ["advocate", "company-secretary"]),
    ("Hospitality Net", "https://www.hospitalitynet.org/news/global.xml", ["hotel-manager"]),
    ("ScienceDaily fitness", "https://www.sciencedaily.com/rss/health_medicine/fitness.xml", ["physical-education-teacher", "physiotherapist"]),
    ("Defense News", "https://www.defensenews.com/arc/outboundfeeds/rss/", ["defence-officer"]),
]
ITEMS_PER_FEED = 8
MAX_FEED_BYTES = 3 * 1024 * 1024
KEEP_DAYS = 60
ATOM = "{http://www.w3.org/2005/Atom}"
OLDEST = datetime(1970, 1, 1, tzinfo=UTC)


def parse_date(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        try:
            value = parsedate_to_datetime(text)        # RSS dates
        except (TypeError, ValueError):
            value = datetime.fromisoformat(text)       # Atom dates
    except (TypeError, ValueError):
        return None
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def parse_feed(xml_bytes: bytes) -> list[dict]:
    """Returns {title, link, published} from RSS or Atom. Only https links are kept."""
    root = ET.fromstring(xml_bytes)
    items = []
    for entry in root.iter("item"):
        items.append({
            "title": entry.findtext("title", ""), "link": entry.findtext("link", ""),
            "published": parse_date(entry.findtext("pubDate")),
        })
    for entry in root.iter(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link[@rel='alternate']")
        if link is None:
            link = entry.find(f"{ATOM}link")
        items.append({
            "title": entry.findtext(f"{ATOM}title", ""),
            "link": link.get("href", "") if link is not None else "",
            "published": parse_date(entry.findtext(f"{ATOM}updated")),
        })
    return [
        {**item, "title": item["title"].strip()[:300], "link": item["link"].strip()}
        for item in items
        if item["title"].strip() and item["link"].strip().startswith("https://") and len(item["link"].strip()) <= 500
    ]


def main() -> None:
    added = 0
    with SessionLocal() as db:
        for source, url, careers in FEEDS:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "CareerPath/1.0", "Accept-Encoding": "identity"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    items = parse_feed(response.read(MAX_FEED_BYTES))
            except (OSError, ET.ParseError) as error:
                print(f"{source}: skipped ({error})")   # one broken feed must never stop the others
                continue
            newest = sorted(items, key=lambda item: item["published"] or OLDEST, reverse=True)
            for item in newest[:ITEMS_PER_FEED]:
                found = db.scalar(select(TechnologyUpdate).where(TechnologyUpdate.link == item["link"]))
                if found is not None:
                    found.careers = careers
                else:
                    db.add(TechnologyUpdate(
                        title=item["title"], link=item["link"], source_name=source, published_at=item["published"], careers=careers,
                    ))
                    added += 1
            db.commit()
        cutoff = datetime.now(UTC) - timedelta(days=KEEP_DAYS)
        removed = db.execute(delete(TechnologyUpdate).where(
            ~TechnologyUpdate.is_tool, TechnologyUpdate.created_at < cutoff,
        )).rowcount
        db.commit()
    print(f"Added {added} new items, removed {removed} old ones.")


if __name__ == "__main__":
    main()
