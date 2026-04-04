from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_zone_queues(df: pd.DataFrame) -> pd.DataFrame:
    """Predict next-hour queue minutes by zone using a simple regression baseline."""
    if df.empty:
        return pd.DataFrame(columns=["zone", "predicted_queue_minutes"])

    model_df = df.copy()
    model_df["hour"] = model_df["time"].str.slice(0, 2).astype(int)

    # Queue proxy for training target.
    model_df["queue_minutes"] = (
        (model_df["visitors"] * 1.4)
        + (model_df["booked_capacity"] / model_df["max_capacity"] * 25)
        + (model_df["incident_count"] * 6)
    ).clip(lower=5, upper=120)

    features = pd.get_dummies(
        model_df[["zone", "hour", "visitors", "booked_capacity", "incident_count"]],
        columns=["zone"],
        dtype=float,
    )
    target = model_df["queue_minutes"].astype(float)

    model = LinearRegression()
    model.fit(features, target)

    next_hour = (int(model_df["hour"].max()) + 1) % 24
    zones = sorted(model_df["zone"].dropna().unique().tolist())

    base_visitors = float(model_df["visitors"].mean())
    base_booked = float(model_df["booked_capacity"].mean())
    base_incidents = float(model_df["incident_count"].mean())

    future = pd.DataFrame(
        {
            "zone": zones,
            "hour": [next_hour] * len(zones),
            "visitors": [base_visitors] * len(zones),
            "booked_capacity": [base_booked] * len(zones),
            "incident_count": [base_incidents] * len(zones),
        }
    )

    future_features = pd.get_dummies(
        future,
        columns=["zone"],
        dtype=float,
    )
    future_features = future_features.reindex(columns=features.columns, fill_value=0.0)

    preds = model.predict(future_features).clip(min=5)

    out = pd.DataFrame({"zone": zones, "predicted_queue_minutes": preds.round(1)})

    def _risk_band(minutes: float) -> str:
        if minutes >= 45:
            return "High"
        if minutes >= 25:
            return "Medium"
        return "Low"

    out["risk_level"] = out["predicted_queue_minutes"].map(_risk_band)
    out["sla_breach"] = out["predicted_queue_minutes"] >= 35

    return out.sort_values("predicted_queue_minutes", ascending=False).reset_index(drop=True)
