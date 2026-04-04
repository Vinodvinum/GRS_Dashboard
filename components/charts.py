from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def revenue_trend(df: pd.DataFrame, period: str = "Daily") -> go.Figure:
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
    freq = freq_map.get(period, "D")

    trend = (
        df.set_index("date")
        .resample(freq)
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
        .reset_index()
    )

    trend["moving_avg"] = trend["revenue"].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend["date"],
            y=trend["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color="#a78bfa", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend["date"],
            y=trend["moving_avg"],
            mode="lines",
            name="Moving Avg (3)",
            line=dict(color="#22d3ee", width=2, dash="dot"),
        )
    )

    fig.update_layout(
        title=f"{period} Revenue Trend",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Date",
        yaxis_title="Revenue",
    )
    return fig


def ticket_type_performance(df: pd.DataFrame) -> go.Figure:
    by_ticket = (
        df.groupby("ticket_type", as_index=False)
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        by_ticket,
        x="ticket_type",
        y="revenue",
        color="ticket_type",
        title="Ticket Type Performance",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def day_wise_traffic(df: pd.DataFrame) -> go.Figure:
    traffic = (
        df.assign(day=df["date"].dt.day_name())
        .groupby("day", as_index=False)
        .agg(visitors=("visitors", "sum"))
    )

    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    traffic["day"] = pd.Categorical(traffic["day"], categories=order, ordered=True)
    traffic = traffic.sort_values("day")

    fig = px.line(
        traffic,
        x="day",
        y="visitors",
        markers=True,
        title="Day-wise Visitor Traffic",
        template="plotly_dark",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def peak_hours_heatmap(df: pd.DataFrame) -> go.Figure:
    temp = df.copy()
    temp["day"] = temp["date"].dt.day_name()
    temp["hour"] = temp["time"].str.slice(0, 2).astype(int)

    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    temp["day"] = pd.Categorical(temp["day"], categories=order, ordered=True)

    pivot = temp.pivot_table(values="visitors", index="day", columns="hour", aggfunc="sum", fill_value=0)

    fig = px.imshow(
        pivot,
        labels=dict(x="Hour", y="Day", color="Visitors"),
        color_continuous_scale=["#111827", "#7c3aed", "#f97316"],
        title="Peak Hours Heatmap",
        template="plotly_dark",
        aspect="auto",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def forecast_chart(history: pd.DataFrame, forecast: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["revenue"],
            mode="lines+markers",
            name="Historical Revenue",
            line=dict(color="#c4b5fd", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["date"],
            y=forecast["predicted_revenue"],
            mode="lines+markers",
            name="Next 7 Days Forecast",
            line=dict(color="#f97316", width=2, dash="dash"),
        )
    )
    if {"lower_bound", "upper_bound"}.issubset(forecast.columns):
        fig.add_trace(
            go.Scatter(
                x=forecast["date"],
                y=forecast["upper_bound"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast["date"],
                y=forecast["lower_bound"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(249, 115, 22, 0.18)",
                name="Forecast Range",
                hoverinfo="skip",
            )
        )
    fig.update_layout(
        title="Revenue Forecast",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Revenue",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def anomaly_timeline(anomaly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=anomaly_df["date"],
            y=anomaly_df["revenue"],
            mode="lines+markers",
            name="Daily Revenue",
            line=dict(color="#a78bfa", width=2),
        )
    )

    flagged = anomaly_df[anomaly_df["is_anomaly"]]
    if not flagged.empty:
        fig.add_trace(
            go.Scatter(
                x=flagged["date"],
                y=flagged["revenue"],
                mode="markers",
                name="Anomaly",
                marker=dict(color="#ef4444", size=10, symbol="diamond"),
            )
        )

    fig.update_layout(
        title="Revenue Anomaly Timeline",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Revenue",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def revenue_stream_breakdown(df: pd.DataFrame) -> go.Figure:
    streams = pd.DataFrame(
        {
            "stream": ["Tickets", "Food", "Merchandise", "Rentals"],
            "revenue": [
                float(df["ticket_revenue"].sum()),
                float(df["food_revenue"].sum()),
                float(df["merch_revenue"].sum()),
                float(df["rental_revenue"].sum()),
            ],
        }
    )
    fig = px.bar(
        streams,
        x="stream",
        y="revenue",
        color="stream",
        title="Revenue by Stream",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def adult_child_split(df: pd.DataFrame) -> go.Figure:
    split = (
        df[df["ticket_type"].isin(["Adult", "Child"])]
        .groupby("ticket_type", as_index=False)
        .agg(visitors=("visitors", "sum"))
    )
    fig = px.pie(
        split,
        names="ticket_type",
        values="visitors",
        hole=0.45,
        title="Adult vs Child Visitor Split",
        template="plotly_dark",
    )
    return fig


def entry_time_distribution(df: pd.DataFrame) -> go.Figure:
    by_hour = (
        df.assign(hour=df["time"].str.slice(0, 2).astype(int))
        .groupby("hour", as_index=False)
        .agg(visitors=("visitors", "sum"))
    )
    fig = px.bar(
        by_hour,
        x="hour",
        y="visitors",
        title="Entry Time Distribution",
        template="plotly_dark",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def combo_offer_impact(df: pd.DataFrame) -> go.Figure:
    combo = (
        df.assign(combo_label=df["is_combo"].map({True: "Combo", False: "Regular"}))
        .groupby("combo_label", as_index=False)
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
    )
    fig = px.bar(
        combo,
        x="combo_label",
        y="revenue",
        color="combo_label",
        title="Combo Offer Impact",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def capacity_utilization_chart(df: pd.DataFrame) -> go.Figure:
    cap = (
        df.assign(day=df["date"].dt.date)
        .groupby("day", as_index=False)
        .agg(booked=("booked_capacity", "mean"), max_capacity=("max_capacity", "mean"))
    )
    cap["utilization_pct"] = (cap["booked"] / cap["max_capacity"]).fillna(0) * 100

    fig = px.line(
        cap,
        x="day",
        y="utilization_pct",
        markers=True,
        title="Capacity Utilization by Day",
        template="plotly_dark",
    )
    fig.update_layout(yaxis_title="Utilization %", margin=dict(l=10, r=10, t=50, b=10))
    return fig


def food_top_items_chart(df: pd.DataFrame) -> go.Figure:
    food = (
        df.groupby("food_item", as_index=False)
        .agg(food_revenue=("food_revenue", "sum"))
        .sort_values("food_revenue", ascending=False)
        .head(8)
    )
    fig = px.bar(
        food,
        x="food_item",
        y="food_revenue",
        color="food_item",
        title="Top Food Items by Revenue",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def marketing_offer_usage_chart(df: pd.DataFrame) -> go.Figure:
    offers = (
        df.groupby("offer_type", as_index=False)
        .agg(revenue=("revenue", "sum"), visitors=("visitors", "sum"))
        .sort_values("revenue", ascending=False)
    )
    fig = px.bar(
        offers,
        x="offer_type",
        y="visitors",
        color="offer_type",
        title="Offer Usage and Conversion Proxy",
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def booking_pipeline_funnel(pipeline_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Funnel(
            y=pipeline_df["stage"],
            x=pipeline_df["count"],
            textposition="inside",
            marker=dict(color=["#8b5cf6", "#7c3aed", "#6d28d9", "#4c1d95"]),
        )
    )
    fig.update_layout(
        title="Corporate and School Booking Pipeline",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def queue_prediction_chart(queue_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        queue_df,
        x="zone",
        y="predicted_queue_minutes",
        color="risk_level",
        color_discrete_map={"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"},
        title="Predicted Queue by Zone (Next Hour)",
        template="plotly_dark",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), xaxis_title="Zone", yaxis_title="Minutes")
    return fig
