from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TicketType:
    name: str
    avg_visitors: int
    price: int


TICKETS = (
    TicketType("Adult", avg_visitors=10, price=1297),
    TicketType("Child", avg_visitors=8, price=1167),
    TicketType("VIP", avg_visitors=4, price=2200),
)

FOOD_ITEMS = (
    ("Burger Combo", 320),
    ("Pizza Slice", 220),
    ("Hot Chocolate", 180),
    ("Fries", 140),
    ("Family Meal", 680),
)

OFFERS = ("None", "Birthday", "Corporate", "Student", "Combo")
SLOTS = ("10:30-12:30", "12:30-14:30", "14:30-16:30", "16:30-18:30")
ZONES = ("Snow Arena", "Kids Zone", "Adventure Rides", "Food Court", "Merch Store")


def _hour_probability() -> tuple[np.ndarray, np.ndarray]:
    hours = np.array([9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    probs = np.array([0.04, 0.08, 0.11, 0.14, 0.13, 0.1, 0.12, 0.11, 0.09, 0.06, 0.02])
    return hours, probs / probs.sum()


def generate_dataset(output_path: str | Path, days: int = 240, seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end_day = datetime.now().date()
    start_day = end_day - timedelta(days=days - 1)

    hours, probs = _hour_probability()
    rows: list[dict[str, object]] = []

    for i in range(days):
        current_day = start_day + timedelta(days=i)
        is_weekend = current_day.weekday() >= 5
        season_factor = 1.2 if current_day.month in (4, 5, 10, 11, 12) else 1.0
        weekend_factor = 1.35 if is_weekend else 1.0

        for ticket in TICKETS:
            tx_count = int(rng.integers(6, 13))
            for _ in range(tx_count):
                hour = int(rng.choice(hours, p=probs))
                minute = int(rng.integers(0, 60))
                visitors = max(
                    1,
                    int(
                        round(
                            rng.poisson(ticket.avg_visitors)
                            * weekend_factor
                            * season_factor
                            * rng.uniform(0.8, 1.2)
                        )
                    ),
                )
                ticket_revenue = visitors * ticket.price

                food_item, food_price = FOOD_ITEMS[int(rng.integers(0, len(FOOD_ITEMS)))]
                food_orders = int(max(0, round(visitors * rng.uniform(0.35, 0.9))))
                food_revenue = food_orders * food_price

                merchandise_revenue = int(round(visitors * rng.uniform(40, 190)))
                rental_revenue = int(round(visitors * rng.uniform(25, 130)))

                offer_type = str(rng.choice(OFFERS, p=[0.52, 0.08, 0.1, 0.12, 0.18]))
                is_combo = offer_type == "Combo"
                discount_pct = 0.12 if is_combo else (0.07 if offer_type in ("Student", "Birthday") else 0.0)

                gross_revenue = ticket_revenue + food_revenue + merchandise_revenue + rental_revenue
                net_revenue = int(round(gross_revenue * (1 - discount_pct)))

                max_capacity = int(rng.choice([220, 240, 260]))
                booked_capacity = min(max_capacity, int(round(visitors * rng.uniform(0.6, 1.05))))

                incident_count = int(rng.choice([0, 0, 0, 1, 1, 2], p=[0.65, 0.12, 0.08, 0.08, 0.05, 0.02]))
                ride_status = str(rng.choice(["Active", "Maintenance"], p=[0.92, 0.08]))
                staff_on_duty = int(rng.integers(18, 42))

                customer_id = int(rng.integers(10000, 99999))
                is_repeat = bool(rng.choice([True, False], p=[0.28, 0.72]))

                rows.append(
                    {
                        "date": current_day.strftime("%Y-%m-%d"),
                        "time": f"{hour:02d}:{minute:02d}:00",
                        "ticket_type": ticket.name,
                        "offer_type": offer_type,
                        "is_combo": is_combo,
                        "food_item": food_item,
                        "slot": str(rng.choice(SLOTS)),
                        "zone": str(rng.choice(ZONES)),
                        "customer_id": customer_id,
                        "is_repeat": is_repeat,
                        "max_capacity": max_capacity,
                        "booked_capacity": booked_capacity,
                        "ride_status": ride_status,
                        "incident_count": incident_count,
                        "staff_on_duty": staff_on_duty,
                        "visitors": visitors,
                        "ticket_revenue": ticket_revenue,
                        "food_revenue": food_revenue,
                        "merch_revenue": merchandise_revenue,
                        "rental_revenue": rental_revenue,
                        "revenue": net_revenue,
                    }
                )

    df = pd.DataFrame(rows).sort_values(["date", "time"]).reset_index(drop=True)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "dataset.csv"
    frame = generate_dataset(path)
    print(f"Generated {len(frame)} rows in {path}")
