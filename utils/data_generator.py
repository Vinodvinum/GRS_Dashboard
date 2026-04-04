from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TicketConfig:
    name: str
    price: int
    demand_multiplier: float


TICKET_CONFIGS = (
    TicketConfig("Adult", 1200, 1.0),
    TicketConfig("Child", 800, 0.85),
    TicketConfig("VIP", 2200, 0.35),
)


def _weighted_hour(rng: np.random.Generator) -> int:
    """Return an hour weighted toward typical park rush periods."""
    slots = np.array([9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    weights = np.array([0.05, 0.08, 0.11, 0.13, 0.12, 0.11, 0.12, 0.1, 0.09, 0.06, 0.03])
    return int(rng.choice(slots, p=weights / weights.sum()))


def generate_dataset(
    output_path: str | Path,
    days: int = 180,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic ticket sales data for a theme park."""
    rng = np.random.default_rng(seed)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    rows: list[dict[str, object]] = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        weekday = current_date.weekday()
        is_weekend = weekday >= 5
        seasonal_boost = 1.15 if current_date.month in (4, 5, 10, 11, 12) else 1.0
        weekend_boost = 1.35 if is_weekend else 1.0

        for ticket in TICKET_CONFIGS:
            transactions = int(rng.integers(6, 12))

            for _ in range(transactions):
                hour = _weighted_hour(rng)
                minute = int(rng.integers(0, 60))
                dt = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    hour,
                    minute,
                )

                base_visitors = rng.poisson(8)
                visitors = max(
                    1,
                    int(
                        round(
                            base_visitors
                            * ticket.demand_multiplier
                            * weekend_boost
                            * seasonal_boost
                        )
                    ),
                )
                revenue = visitors * ticket.price

                rows.append(
                    {
                        "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "ticket_type": ticket.name,
                        "price": ticket.price,
                        "visitors": visitors,
                        "revenue": revenue,
                    }
                )

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


if __name__ == "__main__":
    default_path = Path(__file__).resolve().parents[1] / "data" / "dataset.csv"
    generated = generate_dataset(default_path)
    print(f"Generated {len(generated)} rows at {default_path}")
