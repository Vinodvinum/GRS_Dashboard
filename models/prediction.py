from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def forecast_next_7_days(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = (
        df.set_index("date")
        .resample("D")
        .agg(revenue=("revenue", "sum"))
        .reset_index()
    )

    if daily.empty:
        return daily, pd.DataFrame(columns=["date", "predicted_revenue", "lower_bound", "upper_bound"])

    y = daily["revenue"].to_numpy(dtype=float)
    x = np.arange(len(daily)).reshape(-1, 1)

    if len(daily) >= 2:
        model = LinearRegression()
        model.fit(x, y)
        fitted = model.predict(x)
        residual_std = float(np.std(y - fitted))
        future_x = np.arange(len(daily), len(daily) + 7).reshape(-1, 1)
        preds = model.predict(future_x)
    else:
        residual_std = 0.0
        preds = np.repeat(y[-1], 7)

    preds = np.maximum(preds, 0)
    future_dates = pd.date_range(daily["date"].max() + pd.Timedelta(days=1), periods=7, freq="D")

    forecast = pd.DataFrame(
        {
            "date": future_dates,
            "predicted_revenue": preds,
            "lower_bound": np.maximum(preds - 1.28 * residual_std, 0),
            "upper_bound": preds + 1.28 * residual_std,
        }
    )

    return daily, forecast
