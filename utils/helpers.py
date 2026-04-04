from __future__ import annotations

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

from data.generator import generate_dataset


REQUIRED_COLUMNS = {
    "date",
    "time",
    "ticket_type",
    "offer_type",
    "is_combo",
    "food_item",
    "slot",
    "zone",
    "customer_id",
    "is_repeat",
    "max_capacity",
    "booked_capacity",
    "ride_status",
    "incident_count",
    "staff_on_duty",
    "visitors",
    "ticket_revenue",
    "food_revenue",
    "merch_revenue",
    "rental_revenue",
    "revenue",
}


def ensure_dataset(data_path: Path) -> None:
    if not data_path.exists():
        generate_dataset(data_path)
        return

    df = pd.read_csv(data_path, nrows=5)
    if not REQUIRED_COLUMNS.issubset(df.columns):
        generate_dataset(data_path)



def load_dataset(data_path: Path) -> pd.DataFrame:
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    df["timestamp"] = pd.to_datetime(df["date"].dt.strftime("%Y-%m-%d") + " " + df["time"].astype(str))
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df



def append_live_record(data_path: Path) -> None:
    df = pd.read_csv(data_path)

    rng = np.random.default_rng()
    ticket_type = str(rng.choice(["Adult", "Child", "VIP"], p=[0.47, 0.38, 0.15]))
    visitor_base = {"Adult": 10, "Child": 8, "VIP": 4}
    price_map = {"Adult": 1297, "Child": 1167, "VIP": 2200}
    food_menu = {
        "Burger Combo": 320,
        "Pizza Slice": 220,
        "Hot Chocolate": 180,
        "Fries": 140,
        "Family Meal": 680,
    }

    visitors = max(1, int(rng.poisson(visitor_base[ticket_type])))
    now = pd.Timestamp.now()

    offer_type = str(rng.choice(["None", "Birthday", "Corporate", "Student", "Combo"], p=[0.5, 0.08, 0.12, 0.12, 0.18]))
    is_combo = offer_type == "Combo"
    food_item = str(rng.choice(list(food_menu.keys())))
    food_orders = int(max(0, round(visitors * rng.uniform(0.35, 0.85))))

    ticket_revenue = visitors * price_map[ticket_type]
    food_revenue = food_orders * food_menu[food_item]
    merch_revenue = int(round(visitors * rng.uniform(45, 170)))
    rental_revenue = int(round(visitors * rng.uniform(20, 110)))

    discount_pct = 0.12 if is_combo else (0.07 if offer_type in ("Student", "Birthday") else 0.0)
    gross_revenue = ticket_revenue + food_revenue + merch_revenue + rental_revenue
    net_revenue = int(round(gross_revenue * (1 - discount_pct)))

    max_capacity = int(rng.choice([220, 240, 260]))
    booked_capacity = min(max_capacity, int(round(visitors * rng.uniform(0.6, 1.05))))

    new_row = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "ticket_type": ticket_type,
        "offer_type": offer_type,
        "is_combo": is_combo,
        "food_item": food_item,
        "slot": str(rng.choice(["10:30-12:30", "12:30-14:30", "14:30-16:30", "16:30-18:30"])),
        "zone": str(rng.choice(["Snow Arena", "Kids Zone", "Adventure Rides", "Food Court", "Merch Store"])),
        "customer_id": int(rng.integers(10000, 99999)),
        "is_repeat": bool(rng.choice([True, False], p=[0.3, 0.7])),
        "max_capacity": max_capacity,
        "booked_capacity": booked_capacity,
        "ride_status": str(rng.choice(["Active", "Maintenance"], p=[0.92, 0.08])),
        "incident_count": int(rng.choice([0, 0, 1, 1, 2], p=[0.7, 0.15, 0.08, 0.05, 0.02])),
        "staff_on_duty": int(rng.integers(18, 42)),
        "visitors": visitors,
        "ticket_revenue": ticket_revenue,
        "food_revenue": food_revenue,
        "merch_revenue": merch_revenue,
        "rental_revenue": rental_revenue,
        "revenue": net_revenue,
    }

    updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    updated.to_csv(data_path, index=False)



def filter_dataset(
    df: pd.DataFrame,
    start_date,
    end_date,
    selected_ticket_types: list[str],
) -> pd.DataFrame:
    out = df[
        (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
        & (df["ticket_type"].isin(selected_ticket_types))
    ].copy()

    out["date"] = out["timestamp"]
    return out


def build_booking_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    corporate = int(df.loc[df["offer_type"] == "Corporate", "visitors"].sum())
    school = int(df.loc[df["offer_type"] == "Student", "visitors"].sum())
    base = max(corporate + school, 100)

    qualified = int(round(base * 0.72))
    proposal = int(round(qualified * 0.61))
    confirmed = int(round(proposal * 0.67))

    return pd.DataFrame(
        {
            "stage": ["Leads", "Qualified", "Proposal", "Confirmed"],
            "count": [base, qualified, proposal, confirmed],
        }
    )


def export_daily_mis_snapshot(df: pd.DataFrame, folder: Path) -> tuple[Path, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    stamp = now.strftime("%Y%m%d")

    today = pd.Timestamp(now.date())
    today_df = df[df["date"].dt.date == today.date()].copy()
    if today_df.empty:
        today_df = df.tail(250).copy()

    csv_path = folder / f"mis_snapshot_{stamp}.csv"
    txt_path = folder / f"mis_snapshot_{stamp}.txt"

    today_df.to_csv(csv_path, index=False)

    total_revenue = float(today_df["revenue"].sum())
    visitors = int(today_df["visitors"].sum())
    incidents = int(today_df["incident_count"].sum())
    top_offer = (
        today_df.groupby("offer_type", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
        .head(1)
    )
    top_offer_name = str(top_offer.iloc[0]["offer_type"]) if not top_offer.empty else "N/A"

    summary = [
        f"Date: {now.strftime('%Y-%m-%d')}",
        f"Total Revenue: Rs {total_revenue:,.0f}",
        f"Total Visitors: {visitors:,}",
        f"Total Incidents: {incidents}",
        f"Top Offer: {top_offer_name}",
    ]
    txt_path.write_text("\n".join(summary), encoding="utf-8")

    return csv_path, txt_path
