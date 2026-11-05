"""Create messy retail data in data/raw/. Run: python make_data.py"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

rng = random.Random(42)
CITIES = ["Paris", "Lyon", "Marseille", "Lille", "Nantes", "Bordeaux"]
CATEGORIES = ["fresh", "dairy", "bakery", "drinks", "household"]
CHANNELS = ["web", "app", "store"]
FIRST = ["Amine", "Sara", "Lucas", "Emma", "Youssef", "Lina", "Hugo", "Nadia", "Tom", "Ines"]
LAST = ["Martin", "Bernard", "Benali", "Dubois", "Haddad", "Moreau", "Laurent", "Cherkaoui"]
START, END = date(2024, 1, 1), date(2024, 12, 31)


def rand_date(a, b):
    return a + timedelta(days=rng.randint(0, (b - a).days))


def messy_amount(x):
    r = rng.random()
    if r < 0.10:
        return f"{x:.2f}".replace(".", ",")
    if r < 0.15:
        return f"{x:.2f} €"
    return f"{x:.2f}"


def messy_date(d):
    r = rng.random()
    if r < 0.15:
        return d.strftime("%d/%m/%Y")
    if r < 0.25:
        return f"{d.day} {d.strftime('%b')} {d.year}"
    return d.isoformat()


customers, orders = [], []
for i in range(1, 2001):
    cid = f"C{i:04d}"
    first, last = rng.choice(FIRST), rng.choice(LAST)
    city = rng.choice(CITIES)
    signup = rand_date(date(2023, 1, 1), date(2024, 5, 31))
    rate = rng.uniform(0.6, 4.0)            # orders per month
    late_p = rng.uniform(0.05, 0.45)         # chance a delivery is late
    churn_p = min(0.9, 0.05 + 1.1 * late_p + (0.15 if rate < 1.5 else 0))
    churns = rng.random() < churn_p
    first_day = max(START, signup)
    last_day = rand_date(date(2024, 7, 15), date(2024, 9, 30)) if churns else END
    months = max(1, (last_day - first_day).days // 30)
    for _ in range(int(rate * months)):
        d = rand_date(first_day, last_day)
        late = rng.random() < (late_p * (1.5 if churns else 1))
        orders.append({
            "order_id": f"O{len(orders)+1:06d}", "customer_id": cid,
            "order_date": d, "amount": round(rng.lognormvariate(3.4, 0.5), 2),
            "category": rng.choice(CATEGORIES), "channel": rng.choice(CHANNELS),
            "delivery_days": rng.randint(4, 7) if late else rng.randint(1, 3)})
    name = f"{first} {last}"
    email = f"{first}.{last}@mail.com".lower()
    if rng.random() < 0.03:
        email = email.replace("@", "")       # broken email
    if rng.random() < 0.20:
        name = f"  {name.upper()} "           # messy name
    if rng.random() < 0.05:
        city = ""                            # missing city
    customers.append({"customer_id": cid, "name": name, "email": email.upper() if rng.random() < .1 else email,
                      "city": city, "signup_date": messy_date(signup)})

# real-world mess: duplicate customer rows
customers += rng.sample(customers, 40)
rng.shuffle(customers)

out = Path("data/raw")
out.mkdir(parents=True, exist_ok=True)
with open(out / "customers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(customers[0]))
    w.writeheader()
    w.writerows(customers)

halves = {"h1": [o for o in orders if o["order_date"].month <= 6],
          "h2": [o for o in orders if o["order_date"].month > 6]}
for name, rows in halves.items():
    with open(out / f"orders_2024_{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(orders[0]))
        w.writeheader()
        for k, o in enumerate(rows):
            o = dict(o)
            o["amount"] = messy_amount(-o["amount"] if k % 97 == 0 else o["amount"])   # a few negatives
            o["order_date"] = messy_date(o["order_date"]) if k % 211 else "31/02/2024"  # a few impossible dates
            if k % 150 == 0:
                o["customer_id"] = "C9999"                                              # unknown customer
            w.writerow(o)
print(f"customers: {len(customers)} rows, orders: {len(orders)} rows")
