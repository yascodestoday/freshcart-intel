"""Read the raw files, clean them, write data/clean/. Run: python -m shopintel.ingest"""
import csv
import json
import logging
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from shopintel.cleaning import clean_name, parse_amount, parse_date, valid_email
from shopintel.models import Customer, Order

log = logging.getLogger("ingest")
RAW, CLEAN = Path("data/raw"), Path("data/clean")


def read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}. Did you run python scripts/make_data.py?")


def clean_customers(rows):
    """Return (customers, rejected) where rejected counts the reason."""
    seen, good, rejected = set(), [], Counter()
    for row in rows:
        if row["customer_id"] in seen:
            rejected["duplicate"] += 1
            continue
        signup = parse_date(row["signup_date"])
        if signup is None:
            rejected["bad_date"] += 1
            continue
        seen.add(row["customer_id"])
        email = row["email"].strip().lower()
        good.append(Customer(
            customer_id=row["customer_id"], name=clean_name(row["name"]),
            email=email if valid_email(email) else "",
            city=row["city"].strip().title() or "Unknown", signup_date=signup))
    return good, rejected


def clean_orders(rows, known_ids):
    good, rejected = [], Counter()
    for row in rows:
        day, amount = parse_date(row["order_date"]), parse_amount(row["amount"])
        if day is None:
            rejected["bad_date"] += 1
        elif amount is None or amount <= 0:
            rejected["bad_amount"] += 1
        elif row["customer_id"] not in known_ids:
            rejected["unknown_customer"] += 1
        else:
            good.append(Order(row["order_id"], row["customer_id"], day, amount,
                              row["category"], row["channel"], int(row["delivery_days"])))
    return good, rejected


def write_rows(path, items):
    """Write a list of dataclass objects (Customer or Order) to a CSV file."""
    rows = [asdict(item) for item in items]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    customers, bad_customers = clean_customers(read_rows(RAW / "customers.csv"))
    order_rows = read_rows(RAW / "orders_2024_h1.csv") + read_rows(RAW / "orders_2024_h2.csv")
    known_ids = {c.customer_id for c in customers}
    orders, bad_orders = clean_orders(order_rows, known_ids)

    CLEAN.mkdir(parents=True, exist_ok=True)
    write_rows(CLEAN / "customers.csv", customers)
    write_rows(CLEAN / "orders.csv", orders)
    report = {"customers_kept": len(customers), "customers_rejected": dict(bad_customers),
              "orders_kept": len(orders), "orders_rejected": dict(bad_orders)}
    (CLEAN / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Customers: kept {len(customers)}, rejected {dict(bad_customers)}")
    print(f"Orders:    kept {len(orders)}, rejected {dict(bad_orders)}")
    print(f"Wrote clean files to {CLEAN}/")


if __name__ == "__main__":
    main()
