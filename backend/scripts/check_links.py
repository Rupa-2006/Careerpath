"""
Tests every outside link students can click:  python -m scripts.check_links
Sites that refuse robots are listed separately, because a person needs to open those.
"""
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select

from app.api.journey import web_links
from app.core.database import SessionLocal
from app.models import LearningResource, OpportunitySource, RoadmapStep, Source, TechnologyUpdate

BLOCKED_CODES = {401, 403, 406, 429, 999}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CareerPath link check)"}


def classify(code: int | None) -> str:
    if code is None:
        return "no answer"
    if code < 400:
        return "ok"
    return "blocks robots" if code in BLOCKED_CODES else "broken"


def fetch_status(url: str) -> int | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except OSError:
        return None


def all_links(db) -> list[str]:
    links = set(db.scalars(select(Source.url)))
    links |= set(db.scalars(select(OpportunitySource.url)))
    links |= set(db.scalars(select(LearningResource.url)))
    links |= set(db.scalars(select(TechnologyUpdate.link).where(TechnologyUpdate.is_tool)))
    for resources in db.scalars(select(RoadmapStep.resources)):
        links |= set(web_links(resources))
    return sorted(links)


def main() -> None:
    with SessionLocal() as db:
        links = all_links(db)
    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(fetch_status, links))
    counts: dict[str, int] = {}
    for link, code in zip(links, statuses):
        result = classify(code)
        counts[result] = counts.get(result, 0) + 1
        if result != "ok":
            print(f"{result:14} {code or '-':>4}  {link}")
    print(f"Checked {len(links)} links: {counts}")


if __name__ == "__main__":
    main()
