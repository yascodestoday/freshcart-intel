from datetime import date
from shopintel.models import Order

o = Order("O1", "C1", date(2024, 5, 1), 12.5, "fresh", "web", 5)
print(o)
print(o.is_late)
