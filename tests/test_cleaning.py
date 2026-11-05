from datetime import date

from shopintel.cleaning import clean_name, parse_amount, parse_date, valid_email


def test_clean_name():
    assert clean_name("  SARA   martin ") == "Sara Martin"


def test_parse_amount_formats():
    assert parse_amount("12,50") == 12.5
    assert parse_amount("9.90 €") == 9.9
    assert parse_amount("abc") is None


def test_parse_date_formats():
    assert parse_date("2024-03-05") == date(2024, 3, 5)
    assert parse_date("05/03/2024") == date(2024, 3, 5)
    assert parse_date("5 Mar 2024") == date(2024, 3, 5)
    assert parse_date("31/02/2024") is None


def test_valid_email():
    assert valid_email("a@b.com")
    assert not valid_email("ab.com")
