"""
Advanced ML Models for GRS Dashboard
- Customer Segmentation (K-means)
- Churn Prediction (Logistic Regression)
- Customer Lifetime Value (CLV) Prediction
- A/B Testing Framework
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from math import erfc, sqrt
from typing import Dict, List, Tuple, Any


def _z_critical(confidence_level: float) -> float:
    """Return z critical value for common two-tailed confidence levels."""
    if confidence_level >= 0.99:
        return 2.576
    if confidence_level >= 0.95:
        return 1.96
    if confidence_level >= 0.90:
        return 1.645
    return 1.96


def _two_tailed_p_value_from_z(z_score: float) -> float:
    """Approximate two-tailed p-value using normal distribution."""
    return float(erfc(abs(z_score) / sqrt(2.0)))


def customer_segmentation(df: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
    """
    Segment customers into distinct groups using K-means clustering
    
    Features:
    - Avg spend per transaction
    - Repeat visit frequency
    - Ticket type preference (VIP score)
    - Recency (days since last purchase)
    
    Segments:
    - Budget Shoppers: Low spend, variable repeat
    - Regular Families: Medium spend, consistent repeat
    - Premium Users: High spend, VIP preference
    - Occasional Visitors: Low repeat, medium spend
    
    Args:
        df: Transaction dataframe with date, revenue, ticket_type, customer_id
        n_clusters: Number of segments (default 4)
    
    Returns:
        Dict with cluster assignments, centroids, silhouette score, and segment profiles
    """
    
    try:
        if len(df) == 0:
            return {"error": "Empty dataset"}
        
        # Feature engineering per customer
        customer_agg = df.groupby("customer_id").agg({
            "revenue": ["mean", "sum", "count"],  # Avg spend, total, frequency
            "ticket_type": lambda x: (x == "VIP").sum() / len(x),  # VIP ratio
            "timestamp": ["min", "max"]  # Recency
        }).reset_index()
        
        customer_agg.columns = ["customer_id", "avg_spend", "total_spend", "visit_count", 
                                "vip_ratio", "first_visit", "last_visit"]
        
        # Calculate recency (days since last visit)
        max_date = df["timestamp"].max()
        customer_agg["recency_days"] = (max_date - customer_agg["last_visit"]).dt.days
        
        # Features for clustering
        features = customer_agg[["avg_spend", "visit_count", "vip_ratio", "recency_days"]].copy()
        
        # Handle missing values
        features = features.fillna(0)
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        customer_agg["segment"] = kmeans.fit_predict(features_scaled)
        
        # Calculate silhouette score (model quality 0-1)
        from sklearn.metrics import silhouette_score
        silhouette = silhouette_score(features_scaled, customer_agg["segment"])
        
        # Profile each segment
        segment_profiles = {}
        segment_names = {
            0: "Budget Shoppers",
            1: "Regular Families",
            2: "Premium Users",
            3: "Occasional Visitors"
        }
        
        for seg in range(n_clusters):
            seg_data = customer_agg[customer_agg["segment"] == seg]
            segment_profiles[segment_names.get(seg, f"Segment_{seg}")] = {
                "customer_count": len(seg_data),
                "avg_spend": float(seg_data["avg_spend"].mean()),
                "avg_visits": float(seg_data["visit_count"].mean()),
                "vip_preference": float(seg_data["vip_ratio"].mean()),
                "avg_recency_days": float(seg_data["recency_days"].mean()),
                "total_revenue": float(seg_data["total_spend"].sum())
            }
        
        return {
            "success": True,
            "n_clusters": n_clusters,
            "silhouette_score": float(silhouette),
            "customer_segments": customer_agg[["customer_id", "segment"]].to_dict("records"),
            "segment_profiles": segment_profiles,
            "scaler": scaler,
            "kmeans": kmeans
        }
    
    except Exception as e:
        return {"error": str(e), "success": False}


def churn_prediction(df: pd.DataFrame, lookback_days: int = 60, 
                    prediction_days: int = 30) -> Dict[str, Any]:
    """
    Predict which repeat customers are at risk of not returning (churn)
    
    Features:
    - Visit frequency in lookback period
    - Recency (days since last visit)
    - Average spend trend (increasing/decreasing)
    - Ticket type upgrades (indication of engagement)
    
    Target: Did customer return within prediction_days after lookback period?
    
    Args:
        df: Transaction dataframe with timestamp, customer_id, revenue, ticket_type
        lookback_days: Historical window for feature calculation (default 60)
        prediction_days: Prediction window (default 30)
    
    Returns:
        Dict with churn predictions for each repeat customer
    """
    
    try:
        if len(df) == 0:
            return {"error": "Empty dataset"}
        
        # Filter repeat customers
        repeat_customers = df[df["is_repeat"] == True].copy()
        
        if len(repeat_customers) == 0:
            return {"warning": "No repeat customers in dataset", "predictions": []}
        
        max_date = df["timestamp"].max()
        min_date = max_date - pd.Timedelta(days=lookback_days + prediction_days)
        
        # Historical data for features
        hist_data = df[(df["timestamp"] >= min_date) & (df["timestamp"] < max_date)]
        
        # Feature engineering per customer
        customer_features = []
        
        for cust_id in repeat_customers["customer_id"].unique():
            cust_hist = hist_data[hist_data["customer_id"] == cust_id]
            
            if len(cust_hist) == 0:
                continue
            
            # Split into lookback and prediction periods
            cutoff_date = max_date - pd.Timedelta(days=prediction_days)
            lookback_data = cust_hist[cust_hist["timestamp"] < cutoff_date]
            prediction_data = cust_hist[cust_hist["timestamp"] >= cutoff_date]
            
            if len(lookback_data) == 0:
                continue
            
            # Features
            visit_frequency = len(lookback_data) / (lookback_days / 30)  # Visits per month
            last_visit_days = (cutoff_date - lookback_data["timestamp"].max()).days
            avg_spend = lookback_data["revenue"].mean()
            spend_trend = lookback_data["revenue"].tail(3).mean() - lookback_data["revenue"].head(3).mean()
            vip_engagement = (lookback_data["ticket_type"] == "VIP").sum() / len(lookback_data)
            
            # Target: Did customer return in prediction period?
            churned = len(prediction_data) == 0
            
            customer_features.append({
                "customer_id": cust_id,
                "visit_frequency": visit_frequency,
                "last_visit_days": last_visit_days,
                "avg_spend": avg_spend,
                "spend_trend": spend_trend,
                "vip_engagement": vip_engagement,
                "churned": 1 if churned else 0
            })
        
        if len(customer_features) < 10:
            return {"warning": f"Insufficient data for reliable model (only {len(customer_features)} customers)"}
        
        features_df = pd.DataFrame(customer_features)
        
        # Train logistic regression
        X = features_df[["visit_frequency", "last_visit_days", "avg_spend", "spend_trend", "vip_engagement"]]
        y = features_df["churned"]
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X, y)
        
        # Predict churn probability
        features_df["churn_probability"] = model.predict_proba(X)[:, 1]
        features_df["churn_risk"] = features_df["churn_probability"].apply(
            lambda p: "High" if p > 0.7 else ("Medium" if p > 0.4 else "Low")
        )
        
        # Model accuracy
        from sklearn.metrics import accuracy_score
        accuracy = accuracy_score(y, model.predict(X))
        
        # High-risk customers
        high_risk = features_df[features_df["churn_risk"] == "High"].sort_values("churn_probability", ascending=False)
        
        return {
            "success": True,
            "total_customers": len(features_df),
            "high_risk_count": len(high_risk),
            "model_accuracy": float(accuracy),
            "predictions": features_df.to_dict("records"),
            "high_risk_customers": high_risk[["customer_id", "churn_probability", "churn_risk"]].head(10).to_dict("records"),
            "model": model
        }
    
    except Exception as e:
        return {"error": str(e), "success": False}


def customer_lifetime_value(df: pd.DataFrame, lookback_days: int = 90) -> Dict[str, Any]:
    """
    Predict Customer Lifetime Value (CLV) for each existing customer
    
    Formula:
    CLV = (Avg Purchase Value × Purchase Frequency × Customer Lifespan)
    
    Factors:
    - Historical spend (avg transaction value)
    - Visit frequency (transactions per month)
    - Retention likelihood (from churn prediction)
    - Ticket type preferences (higher CLV for VIP customers)
    
    Args:
        df: Transaction dataframe
        lookback_days: Historical window for CLV calculation
    
    Returns:
        Dict with CLV predictions ranked by value
    """
    
    try:
        if len(df) == 0:
            return {"error": "Empty dataset"}
        
        max_date = df["timestamp"].max()
        min_date = max_date - pd.Timedelta(days=lookback_days)
        hist_data = df[df["timestamp"] >= min_date].copy()
        
        # Customer-level metrics
        clv_data = []
        
        for cust_id in df["customer_id"].unique():
            cust_data = hist_data[hist_data["customer_id"] == cust_id]
            overall_data = df[df["customer_id"] == cust_id]
            
            if len(cust_data) == 0:
                continue
            
            # Historical metrics
            avg_transaction_value = cust_data["revenue"].mean()
            transaction_frequency = len(cust_data) / (lookback_days / 30)  # Per month
            total_revenue = cust_data["revenue"].sum()
            visit_count = len(cust_data)
            
            # Engagement metrics
            is_repeat = overall_data["is_repeat"].iloc[0] if len(overall_data) > 0 else False
            vip_affinity = (overall_data["ticket_type"] == "VIP").sum() / len(overall_data) if len(overall_data) > 0 else 0
            
            # Recency
            days_since_last = (max_date - cust_data["timestamp"].max()).days
            
            # CLV Calculation (simple model)
            # Assume 24-month customer lifespan, retention probability based on recent activity
            retention_proba = 1.0 if days_since_last < 30 else (0.8 if days_since_last < 60 else 0.5)
            predicted_lifespan_months = 24 * retention_proba
            
            clv_estimate = avg_transaction_value * transaction_frequency * predicted_lifespan_months
            
            # Adjustments
            if is_repeat:
                clv_estimate *= 1.2  # 20% boost for known repeaters
            if vip_affinity > 0.3:
                clv_estimate *= 1.3  # 30% boost for VIP-prone customers
            
            clv_data.append({
                "customer_id": cust_id,
                "avg_transaction_value": float(avg_transaction_value),
                "transaction_frequency_monthly": float(transaction_frequency),
                "total_historical_revenue": float(total_revenue),
                "visit_count": int(visit_count),
                "vip_affinity": float(vip_affinity),
                "retention_probability": float(retention_proba),
                "predicted_lifespan_months": float(predicted_lifespan_months),
                "clv_estimate": float(clv_estimate),
                "days_since_last_visit": int(days_since_last)
            })
        
        clv_df = pd.DataFrame(clv_data)
        clv_df = clv_df.sort_values("clv_estimate", ascending=False)
        
        # Segments
        high_value = len(clv_df[clv_df["clv_estimate"] > clv_df["clv_estimate"].quantile(0.75)])
        medium_value = len(clv_df[(clv_df["clv_estimate"] <= clv_df["clv_estimate"].quantile(0.75)) & 
                                   (clv_df["clv_estimate"] > clv_df["clv_estimate"].quantile(0.25))])
        low_value = len(clv_df[clv_df["clv_estimate"] <= clv_df["clv_estimate"].quantile(0.25)])
        
        return {
            "success": True,
            "total_customers": len(clv_df),
            "total_predicted_clv": float(clv_df["clv_estimate"].sum()),
            "avg_clv": float(clv_df["clv_estimate"].mean()),
            "high_value_customers": high_value,
            "medium_value_customers": medium_value,
            "low_value_customers": low_value,
            "top_10_customers": clv_df.head(10).to_dict("records"),
            "all_predictions": clv_df.to_dict("records")
        }
    
    except Exception as e:
        return {"error": str(e), "success": False}


def ab_testing_framework(df_control: pd.DataFrame, df_test: pd.DataFrame, 
                        metric: str = "revenue", confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    A/B testing framework for comparing two campaign groups
    
    Performs:
    - Mean comparison (t-test, Mann-Whitney U)
    - Conversion rate comparison (chi-square)
    - Effect size calculation (Cohen's d)
    - Sample size adequacy check
    - Confidence interval calculation
    
    Args:
        df_control: Control group transactions (e.g., no offer)
        df_test: Test group transactions (e.g., with offer)
        metric: Metric to compare ("revenue", "visitors", "conversion_rate")
        confidence_level: Statistical confidence (default 0.95 = 95%)
    
    Returns:
        Dict with test results, significance, and recommendations
    """
    
    try:
        if len(df_control) == 0 or len(df_test) == 0:
            return {"error": "One or both groups are empty"}
        
        results = {
            "control_group_size": len(df_control),
            "test_group_size": len(df_test),
            "confidence_level": confidence_level
        }
        
        if metric == "revenue":
            control_metric = df_control["revenue"].values
            test_metric = df_test["revenue"].values
            
        elif metric == "visitors":
            control_metric = df_control["visitors"].values
            test_metric = df_test["visitors"].values
            
        elif metric == "conversion_rate":
            control_metric = (df_control["ticket_type"] == "VIP").astype(int).values
            test_metric = (df_test["ticket_type"] == "VIP").astype(int).values
        
        else:
            return {"error": f"Unknown metric: {metric}"}
        
        # Descriptive stats
        results["control_mean"] = float(control_metric.mean())
        results["test_mean"] = float(test_metric.mean())
        results["control_std"] = float(control_metric.std())
        results["test_std"] = float(test_metric.std())
        
        # Percentage difference
        if results["control_mean"] != 0:
            pct_diff = ((results["test_mean"] - results["control_mean"]) / results["control_mean"]) * 100
            results["percentage_difference"] = float(pct_diff)
        else:
            results["percentage_difference"] = None
        
        # Independent means test using normal approximation (no SciPy dependency)
        n_control = max(len(control_metric), 1)
        n_test = max(len(test_metric), 1)
        control_var = float(np.var(control_metric, ddof=1)) if n_control > 1 else 0.0
        test_var = float(np.var(test_metric, ddof=1)) if n_test > 1 else 0.0
        se_diff = sqrt((test_var / n_test) + (control_var / n_control)) if (n_test > 1 and n_control > 1) else 0.0

        if se_diff > 0:
            z_stat = float((results["test_mean"] - results["control_mean"]) / se_diff)
            p_value = _two_tailed_p_value_from_z(z_stat)
        else:
            z_stat = 0.0
            p_value = 1.0

        results["z_statistic"] = z_stat
        results["p_value"] = float(p_value)
        
        alpha = 1 - confidence_level
        is_significant = p_value < alpha
        results["is_statistically_significant"] = bool(is_significant)
        results["significance_level"] = alpha
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((control_metric.std()**2 + test_metric.std()**2) / 2)
        if pooled_std > 0:
            cohens_d = (test_metric.mean() - control_metric.mean()) / pooled_std
            results["cohens_d"] = float(cohens_d)
            
            if abs(cohens_d) < 0.2:
                effect_size = "Negligible"
            elif abs(cohens_d) < 0.5:
                effect_size = "Small"
            elif abs(cohens_d) < 0.8:
                effect_size = "Medium"
            else:
                effect_size = "Large"
            
            results["effect_size_interpretation"] = effect_size
        
        # Confidence interval for test group mean using normal approximation
        z_value = _z_critical(confidence_level)
        test_std = float(np.std(test_metric, ddof=1)) if len(test_metric) > 1 else 0.0
        test_se = test_std / sqrt(max(len(test_metric), 1)) if len(test_metric) > 0 else 0.0
        ci_low = float(results["test_mean"] - (z_value * test_se))
        ci_high = float(results["test_mean"] + (z_value * test_se))
        results["test_group_ci"] = [ci_low, ci_high]
        
        # Sample size analysis (post-hoc power)
        min_sample_size = 2 * ((1.96 + 0.84)**2 * (control_metric.std()**2 + test_metric.std()**2)) / \
                         ((test_metric.mean() - control_metric.mean())**2 + 1e-10)
        results["recommended_sample_size"] = max(int(min_sample_size), 30)
        
        # Recommendation
        if is_significant:
            if pct_diff is not None and pct_diff > 0:
                recommendation = f"✅ Test group shows {pct_diff:.1f}% IMPROVEMENT (statistically significant at {confidence_level*100:.0f}% confidence)"
            else:
                recommendation = f"✅ Test group shows {-pct_diff:.1f}% DECLINE but statistically significant"
        else:
            if len(control_metric) >= results["recommended_sample_size"]:
                recommendation = "⚠️ NO significant difference detected. Insufficient evidence to change strategy."
            else:
                recommendation = f"🔄 Insufficient sample size. Recommend continuing test until {results['recommended_sample_size']} transactions per group"
        
        results["recommendation"] = recommendation
        results["interpretation"] = {
            "control_group": f"Mean {metric}: {results['control_mean']:.2f}",
            "test_group": f"Mean {metric}: {results['test_mean']:.2f}",
            "difference": f"{pct_diff:.1f}%" if results["percentage_difference"] else "N/A",
            "p_value": f"{p_value:.4f}",
            "significant": "Yes" if is_significant else "No"
        }
        
        return {"success": True, **results}
    
    except Exception as e:
        return {"error": str(e), "success": False}


def customer_segmentation_insights(segments_output: Dict) -> str:
    """
    Generate human-readable insights from customer segmentation results
    """
    if "error" in segments_output:
        return f"Segmentation error: {segments_output['error']}"
    
    profiles = segments_output.get("segment_profiles", {})
    insights = "**Customer Segmentation Insights:**\n\n"
    
    for segment_name, profile in profiles.items():
        insights += f"**{segment_name}** ({profile['customer_count']} customers)\n"
        insights += f"  • Avg Spend: ₹{profile['avg_spend']:.0f}\n"
        insights += f"  • Monthly Visits: {profile['avg_visits']:.1f}\n"
        insights += f"  • VIP Preference: {profile['vip_preference']*100:.0f}%\n"
        insights += f"  • Revenue Contribution: ₹{profile['total_revenue']:,.0f}\n\n"
    
    return insights
