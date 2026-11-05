"""Data models for ShopIntel."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

LATE_AFTER_DAYS = 3  # on-time deliveries take 1–3 days, late ones 4–7

@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    city: str
    signup_date: date


@dataclass
class Order:
    order_id: str
    customer_id: str
    order_date: date
    amount: float
    category: str
    channel: str
    delivery_days: int

    @property
    def is_late(self) -> bool:
        return self.delivery_days > LATE_AFTER_DAYS


    def is_fast(self)->bool:
        return self.delivery_days <=1 

