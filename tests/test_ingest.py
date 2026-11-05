from shopintel.ingest import clean_customers, clean_orders


def row(**kw):
    base = {"customer_id": "C1", "name": "ana", "email": "a@b.com", "city": "paris", "signup_date": "2024-01-01"}
    return {**base, **kw}


def test_duplicates_are_rejected():
    good, bad = clean_customers([row(), row()])
    assert len(good) == 1 and bad["duplicate"] == 1


def test_bad_order_rows_are_counted():
    base = {"order_id": "O1", "customer_id": "C1", "order_date": "2024-01-02", "amount": "5",
            "category": "fresh", "channel": "web", "delivery_days": "2"}
    rows = [base, {**base, "amount": "-3"}, {**base, "customer_id": "C9"}, {**base, "order_date": "31/02/2024"}]
    good, bad = clean_orders(rows, {"C1"})
    assert len(good) == 1
    assert bad["bad_amount"] == 1 and bad["unknown_customer"] == 1 and bad["bad_date"] == 1
