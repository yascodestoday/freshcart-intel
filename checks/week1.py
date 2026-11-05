from pathlib import Path

from checks.util import csv_rows, pytest_ok

FILES = ["make_data.py", "shopintel/cleaning.py", "shopintel/models.py", "shopintel/ingest.py",
         "tests/test_cleaning.py", "tests/test_ingest.py", ".gitignore", "README.md"]


def run():
    out = [(f"file {f} exists", Path(f).exists(), "create this file") for f in FILES]
    out.append(("pytest passes", pytest_ok(), "run pytest -q and fix the failures"))
    out.append(("clean customers = 2000 rows", csv_rows("data/clean/customers.csv") == 2000,
                "run python make_data.py then python -m shopintel.ingest"))
    out.append(("clean orders = 42411 rows", csv_rows("data/clean/orders.csv") == 42411,
                "run python -m shopintel.ingest"))
    return out
