from __future__ import annotations

from typing import cast

import numpy as np
import pandas as pd


def generate_business_insights(df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {
            "best_day": "N/A",
            "lowest_day": "N/A",
            "suggestions": ["No data available for insights."],
        }

    day_perf = (
        df.assign(day=df["date"].dt.day_name())
        .groupby("day", as_index=False)
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
    )

    best_idx = int(day_perf["revenue"].idxmax())
    low_idx = int(day_perf["visitors"].idxmin())
    best_day = str(day_perf.at[best_idx, "day"])
    low_day = str(day_perf.at[low_idx, "day"])
    best_revenue = cast(float, day_perf.at[best_idx, "revenue"])
    median_revenue = float(day_perf["revenue"].median())

    weekend_days = ["Saturday", "Sunday"]
    weekday_visitors = day_perf.loc[~day_perf["day"].isin(weekend_days), "visitors"].sum()
    weekend_visitors = day_perf.loc[day_perf["day"].isin(weekend_days), "visitors"].sum()

    suggestions: list[str] = []

    if weekday_visitors < weekend_visitors:
        suggestions.append("Weekdays have lower traffic. Consider promotions and bundled offers.")
    else:
        suggestions.append("Weekday performance is strong. Maintain mid-week campaigns and loyalty programs.")

    if best_revenue > (median_revenue * 1.2):
        suggestions.append(f"{best_day} is the best performing day. Plan premium events on this day.")

    suggestions.append(f"{low_day} has the lowest traffic. Run targeted digital ads for this day.")

    return {
        "best_day": best_day,
        "lowest_day": low_day,
        "suggestions": suggestions,
    }


def detect_daily_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    daily = (
        df.set_index("date")
        .resample("D")
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
        .reset_index()
    )

    if daily.empty or len(daily) < 7:
        daily["is_anomaly"] = False
        daily["z_score"] = 0.0
        return daily

    mean_val = float(daily["revenue"].mean())
    std_val = float(daily["revenue"].std())

    if std_val == 0:
        daily["z_score"] = 0.0
    else:
        daily["z_score"] = (daily["revenue"] - mean_val) / std_val

    daily["is_anomaly"] = daily["z_score"].abs() >= z_threshold
    return daily


def simulate_business_scenario(
    df: pd.DataFrame,
    weekday_uplift_pct: float,
    vip_mix_increase_pct: float,
) -> dict[str, float]:
    revenue_series = df["revenue"].astype(float)
    baseline_revenue = float(revenue_series.sum())
    if baseline_revenue <= 0:
        return {"baseline": 0.0, "simulated": 0.0, "delta": 0.0, "delta_pct": 0.0}

    simulated = df.copy()
    simulated["revenue"] = revenue_series.copy()
    day_name = simulated["date"].dt.day_name()
    weekday_mask = ~day_name.isin(["Saturday", "Sunday"])
    vip_mask = simulated["ticket_type"] == "VIP"

    weekday_factor = 1 + (weekday_uplift_pct / 100.0)
    vip_factor = 1 + (vip_mix_increase_pct / 100.0)

    simulated.loc[weekday_mask, "revenue"] = simulated.loc[weekday_mask, "revenue"] * weekday_factor
    simulated.loc[vip_mask, "revenue"] = simulated.loc[vip_mask, "revenue"] * vip_factor

    simulated_revenue = float(simulated["revenue"].sum())
    delta = simulated_revenue - baseline_revenue
    delta_pct = (delta / baseline_revenue) * 100.0

    return {
        "baseline": baseline_revenue,
        "simulated": simulated_revenue,
        "delta": delta,
        "delta_pct": delta_pct,
    }


def build_executive_summary(df: pd.DataFrame, forecast_df: pd.DataFrame) -> list[str]:
    summary: list[str] = []

    recent = (
        df.set_index("date")
        .resample("D")
        .agg(revenue=("revenue", "sum"))
        .tail(14)
        .reset_index(drop=True)
    )

    if len(recent) >= 10:
        first_half = float(recent["revenue"].head(7).mean())
        second_half = float(recent["revenue"].tail(7).mean())
        if second_half > first_half:
            summary.append("Revenue momentum is positive in the last 2 weeks.")
        else:
            summary.append("Revenue momentum is softening. Review weekday campaigns.")

    if not forecast_df.empty:
        avg_forecast = float(forecast_df["predicted_revenue"].mean())
        summary.append(f"Expected average daily revenue for next 7 days: Rs {avg_forecast:,.0f}.")

    if not summary:
        summary.append("Insufficient data for executive summary.")

    return summary


def management_alerts(df: pd.DataFrame) -> list[str]:
    alerts: list[str] = []

    if df.empty:
        return ["No data available for alerts."]

    weekend_mask = df["date"].dt.dayofweek >= 5
    weekend_rev = float(df.loc[weekend_mask, "revenue"].sum())
    total_rev = float(df["revenue"].sum())
    weekend_share = (weekend_rev / total_rev) * 100 if total_rev else 0.0
    alerts.append(f"Weekends contribute {weekend_share:.1f}% of total revenue.")

    peak_hours = (
        df.assign(hour=df["time"].str.slice(0, 2).astype(int))
        .groupby("hour", as_index=False)
        .agg(visitors=("visitors", "sum"))
        .sort_values("visitors", ascending=False)
        .head(2)
    )
    if len(peak_hours) >= 2:
        h1 = int(peak_hours.iloc[0]["hour"])
        h2 = int(peak_hours.iloc[1]["hour"])
        alerts.append(f"Peak traffic window detected around {h1}:00-{h2 + 1}:00.")

    combo_rev = float(df.loc[df["is_combo"], "revenue"].sum())
    combo_share = (combo_rev / total_rev) * 100 if total_rev else 0.0
    alerts.append(f"Combo-linked transactions drive {combo_share:.1f}% of revenue.")

    over_capacity = (df["booked_capacity"] > df["max_capacity"] * 0.92).sum()
    if int(over_capacity) > 0:
        alerts.append(f"Capacity risk: {int(over_capacity)} records above 92% utilization.")

    return alerts


def customer_behavior_snapshot(df: pd.DataFrame) -> dict[str, float]:
    total_visitors = float(df["visitors"].sum())
    total_revenue = float(df["revenue"].sum())
    avg_spend = total_revenue / total_visitors if total_visitors else 0.0

    repeat_visitors = float(df.loc[df["is_repeat"], "visitors"].sum())
    repeat_ratio = (repeat_visitors / total_visitors) * 100 if total_visitors else 0.0

    high_value_cutoff = float(df["revenue"].quantile(0.8)) if not df.empty else 0.0
    high_value_count = float((df["revenue"] >= high_value_cutoff).sum())

    return {
        "avg_spend": avg_spend,
        "repeat_ratio": repeat_ratio,
        "high_value_count": high_value_count,
    }
