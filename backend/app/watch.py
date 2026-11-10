"""
Watches official pages and tells an admin when they change.

It never changes what students see. A person reads the source, then updates the record.
Pages that can't be read are reported as unreadable, so a blank page never looks like a change.
"""
import difflib
import gzip
import hashlib
import html
import re
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from html.parser import HTMLParser

from sqlalchemy.orm import Session

from app.models import SourceWatch

MAX_PAGE_BYTES = 3 * 1024 * 1024
MIN_READABLE_CHARS = 200
SUMMARY_CHARS = 600
TIMEOUT_SECONDS = 25
# Counters and clocks change on every visit, so they are removed before pages are compared
NOISE = re.compile(r"(no\.? ?of visitors|visitor count|visitors?)\s*:?\s*[\d,]+|last updated\s*:?[^\n]{0,40}|\b\d{1,2}:\d{2}(:\d{2})?\s*(am|pm)?\b", re.I)


# A number alone on a line is a live counter, such as seats or visitors. Dates have other characters, so they stay.
COUNTER = re.compile(r"[\d,.\s₹%+]+")


class TextOnly(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if text and not self.depth:
            self.lines.append(text)


def page_text(raw: str) -> str:
    parser = TextOnly()
    parser.feed(raw)
    lines = (" ".join(NOISE.sub(" ", html.unescape(line)).split()) for line in parser.lines)
    return "\n".join(line for line in lines if line and not COUNTER.fullmatch(line))


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "CareerPath-source-watch/1.0", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed official URLs only
        body = response.read(MAX_PAGE_BYTES)
    if body[:2] == b"\x1f\x8b":   # some sites send compressed pages even when not asked
        body = gzip.decompress(body)
    return body.decode("utf-8", errors="replace")


def what_changed(old: str, new: str) -> str:
    marked = []
    for line in difflib.unified_diff(old.split("\n"), new.split("\n"), lineterm="", n=0):
        if line[:1] in "+-" and line[:3] not in ("+++", "---"):
            marked.append(("Added: " if line[0] == "+" else "Removed: ") + line[1:])
    return "\n".join(marked)[:SUMMARY_CHARS]


# Lines that change on their own (visitor counts, refresh times, totals) are never worth an alert.
NOISE_LINE = re.compile(r"refreshed|visitor|hits\b|page views|crore|lakh|copyright|©|last updated on|server time", re.I)
# Words that usually mean something students care about has changed.
IMPORTANT = re.compile(
    r"notification|eligib|last date|schedule|admission|counsell?ing|\bfee|exam|apply|application|registration|"
    r"result|deadline|brochure|prospectus|booklet|seat|rank|merit|syllabus|guideline|rule|cut-?off|20[2-3]\d", re.I,
)


def is_important(summary: str) -> bool:
    """True when a real line (not noise) mentions dates, rules, admissions or similar."""
    for line in summary.split("\n"):
        text = line.split(": ", 1)[-1]
        if text.strip() and not NOISE_LINE.search(text) and IMPORTANT.search(text):
            return True
    return False


def check_one(watch: SourceWatch, read: Callable[[str], str] = fetch) -> str:
    """Returns one of: new, same, changed, unreadable, failed."""
    watch.last_checked_at = datetime.now(UTC)
    try:
        text = page_text(read(watch.url).replace("\x00", ""))
    except Exception as problem:  # noqa: BLE001 - one broken site must not stop the others
        watch.last_error = str(problem)[:200]
        return "failed"
    if len(text) < MIN_READABLE_CHARS:
        watch.last_error = "The page needs a browser, or it came back nearly empty."
        return "unreadable"
    watch.last_error = None
    digest = hashlib.sha256(text.encode()).hexdigest()
    if watch.content_hash is None:
        watch.content_hash, watch.last_text = digest, text
        return "new"
    if digest == watch.content_hash:
        return "same"
    summary = what_changed(watch.last_text or "", text)
    watch.content_hash, watch.last_text = digest, text
    if not is_important(summary):
        return "minor"   # saved quietly: small changes never ask anyone to look
    watch.change_summary = summary
    watch.last_changed_at, watch.needs_review = datetime.now(UTC), True
    return "changed"


def check_all(db: Session, read: Callable[[str], str] = fetch) -> dict[str, int]:
    counts: dict[str, int] = {}
    for watch in db.query(SourceWatch).order_by(SourceWatch.id).all():
        result = check_one(watch, read)
        try:
            db.commit()
        except Exception:  # noqa: BLE001 - one bad page must not stop the others
            db.rollback()
            result = "failed"
        counts[result] = counts.get(result, 0) + 1
    return counts
