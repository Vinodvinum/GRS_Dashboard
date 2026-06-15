from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    path = Path("data/dataset.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    last_date = df["date"].max().date()
    target_date = date(2026, 6, 15)
    print(f"current last date: {last_date}")
    print(f"target date: {target_date}")

    if last_date >= target_date:
        print("Dataset already reaches target date.")
        return

    rng = np.random.default_rng(20260615)
    hours = np.array([9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    probs = np.array([0.04, 0.08, 0.11, 0.14, 0.13, 0.1, 0.12, 0.11, 0.09, 0.06, 0.02])
    probs = probs / probs.sum()
    tickets = [
        ("Adult", 10, 1297),
        ("Child", 8, 1167),
        ("VIP", 4, 2200),
    ]
    food_items = [
        ("Burger Combo", 320),
        ("Pizza Slice", 220),
        ("Hot Chocolate", 180),
        ("Fries", 140),
        ("Family Meal", 680),
    ]
    offers = ["", "Birthday", "Corporate", "Student", "Combo"]
    offer_probs = np.array([0.52, 0.08, 0.1, 0.12, 0.18])
    slots = ["10:30-12:30", "12:30-14:30", "14:30-16:30", "16:30-18:30"]
    zones = ["Snow Arena", "Kids Zone", "Adventure Rides", "Food Court", "Merch Store"]

    rows: list[dict[str, object]] = []
    current_date = last_date + timedelta(days=1)
    while current_date <= target_date:
        is_weekend = current_date.weekday() >= 5
        season_factor = 1.2 if current_date.month in (4, 5, 10, 11, 12) else 1.0
        weekend_factor = 1.35 if is_weekend else 1.0

        for ticket_name, avg_visitors, price in tickets:
            tx_count = int(rng.integers(6, 13))
            for _ in range(tx_count):
                hour = int(rng.choice(hours, p=probs))
                minute = int(rng.integers(0, 60))
                visitors = max(
                    1,
                    int(
                        round(
                            rng.poisson(avg_visitors)
                            * weekend_factor
                            * season_factor
                            * rng.uniform(0.8, 1.2)
                        )
                    ),
                )
                ticket_revenue = visitors * price

                food_item, food_price = food_items[int(rng.integers(0, len(food_items)))]
                food_orders = int(max(0, round(visitors * rng.uniform(0.35, 0.9))))
                food_revenue = food_orders * food_price

                merch_revenue = int(round(visitors * rng.uniform(40, 190)))
                rental_revenue = int(round(visitors * rng.uniform(25, 130)))

                offer_type = str(rng.choice(offers, p=offer_probs))
                is_combo = offer_type == "Combo"
                discount_pct = 0.12 if is_combo else (0.07 if offer_type in ("Student", "Birthday") else 0.0)

                gross_revenue = ticket_revenue + food_revenue + merch_revenue + rental_revenue
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
                        "date": current_date.strftime("%Y-%m-%d"),
                        "time": f"{hour:02d}:{minute:02d}:00",
                        "ticket_type": ticket_name,
                        "offer_type": offer_type,
                        "is_combo": is_combo,
                        "food_item": food_item,
                        "slot": str(rng.choice(slots)),
                        "zone": str(rng.choice(zones)),
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
                        "merch_revenue": merch_revenue,
                        "rental_revenue": rental_revenue,
                        "revenue": net_revenue,
                    }
                )
        current_date += timedelta(days=1)

    new_df = pd.DataFrame(rows)
    output = pd.concat([df, new_df], ignore_index=True)
    output.to_csv(path, index=False)
    print(f"Appended {len(new_df)} rows.")
    print(f"New dataset range: {output['date'].min().date()} to {output['date'].max().date()}")


if __name__ == '__main__':
    main()
