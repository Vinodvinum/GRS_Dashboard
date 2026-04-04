from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
import streamlit as st


def _safe_growth(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def compute_kpis(
    filtered_df: pd.DataFrame,
    full_df: pd.DataFrame,
    start_date,
    end_date,
    selected_ticket_types: list[str],
) -> dict[str, float]:
    total_revenue = float(filtered_df["revenue"].sum())
    total_visitors = float(filtered_df["visitors"].sum())
    avg_revenue_per_visitor = total_revenue / total_visitors if total_visitors else 0.0

    period_days = max((end_date - start_date).days + 1, 1)
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)

    previous_df = full_df[
        (full_df["date"] >= pd.Timestamp(prev_start))
        & (full_df["date"] <= pd.Timestamp(prev_end) + pd.Timedelta(hours=23, minutes=59))
        & (full_df["ticket_type"].isin(selected_ticket_types))
    ]

    previous_revenue = float(previous_df["revenue"].sum())
    revenue_growth_pct = _safe_growth(total_revenue, previous_revenue)

    return {
        "total_revenue": total_revenue,
        "total_visitors": total_visitors,
        "avg_revenue_per_visitor": avg_revenue_per_visitor,
        "revenue_growth_pct": revenue_growth_pct,
    }


def render_kpi_cards(metrics: dict[str, float]) -> None:
    cards = [
        (
            "Total Revenue",
            f"Rs {metrics['total_revenue']:,.0f}",
            f"{metrics['revenue_growth_pct']:.2f}% vs previous period",
            "💰",
            "#f59e0b",
        ),
        (
            "Total Visitors",
            f"{int(metrics['total_visitors']):,}",
            "Current selected period",
            "👥",
            "#38bdf8",
        ),
        (
            "Avg Revenue / Visitor",
            f"Rs {metrics['avg_revenue_per_visitor']:,.0f}",
            "Spending efficiency",
            "📈",
            "#34d399",
        ),
        (
            "Revenue Growth",
            f"{metrics['revenue_growth_pct']:.2f}%",
            "Momentum indicator",
            "🚀",
            "#a78bfa",
        ),
    ]

    cols = st.columns(4)
    for col, (title, value, delta, icon, accent) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="card-title">{icon} {title}</div>
                    <div class="card-value" style="font-size: 2rem; color: {accent}; text-shadow: 0 0 14px rgba(255,255,255,0.08);">{value}</div>
                    <div class="card-delta">{delta}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
