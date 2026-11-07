"""
Reads the official directory into a batch for review:
    python -m scripts.import_colleges "C:\\path\\All Colleges AISHE Dashboard.xlsx"
Nothing appears on the site until an admin publishes the batch.
"""
import sys
from pathlib import Path

from app.college_import import ImportRefused, stage_file
from app.core.database import SessionLocal


def main() -> None:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        raise SystemExit('Give the path to the file, for example: python -m scripts.import_colleges "colleges.xlsx"')
    with SessionLocal() as db:
        try:
            batch = stage_file(db, Path(sys.argv[1]))
        except ImportRefused as problem:
            raise SystemExit(f"Not imported: {problem}") from None
    print(f"Read {batch.rows_read} rows: {batch.rows_new} new, {batch.rows_changed} changed, "
          f"{batch.rows_unchanged} unchanged, {batch.rows_rejected} rejected, {batch.rows_missing} missing.")
    print("Open Admin on the website to review and publish it.")


if __name__ == "__main__":
    main()
