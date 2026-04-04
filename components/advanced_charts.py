"""
Advanced Charts for GRS Dashboard
- Customer Segment Distribution
- Churn Risk Heatmap
- CLV Distribution & Top Customers
- A/B Test Results
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List


def customer_segment_bubble(segmentation_output: Dict) -> go.Figure:
    """
    Bubble chart showing customer segments
    X-axis: Avg Spend
    Y-axis: Visit Frequency
    Bubble size: Total Revenue
    Color: Segment
    """
    
    try:
        if "error" in segmentation_output:
            fig = go.Figure()
            fig.add_annotation(text="Error in segmentation", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        segments = segmentation_output.get("segment_profiles", {})
        
        data = []
        for segment_name, profile in segments.items():
            data.append({
                "segment": segment_name,
                "avg_spend": profile["avg_spend"],
                "visit_frequency": profile["avg_visits"],
                "total_revenue": profile["total_revenue"],
                "customer_count": profile["customer_count"]
            })
        
        df = pd.DataFrame(data)
        
        fig = px.scatter(df, 
                        x="avg_spend", 
                        y="visit_frequency",
                        size="total_revenue",
                        color="segment",
                        hover_name="segment",
                        hover_data={"customer_count": True, "total_revenue": ":.0f"},
                        title="Customer Segmentation Analysis",
                        labels={"avg_spend": "Avg Spend per Transaction (₹)", 
                               "visit_frequency": "Monthly Visit Frequency"})
        
        fig.update_layout(
            template="plotly_dark",
            hovermode="closest",
            plot_bgcolor="rgba(31, 15, 61, 0.5)",
            paper_bgcolor="rgba(15, 15, 15, 1)"
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


def churn_risk_distribution(churn_output: Dict) -> go.Figure:
    """
    Histogram showing churn probability distribution
    Color-coded by risk level (Low/Medium/High)
    """
    
    try:
        if "error" in churn_output or not churn_output.get("success"):
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for churn prediction", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        predictions = churn_output.get("predictions", [])
        df = pd.DataFrame(predictions)
        
        # Create histogram with risk coloring
        fig = go.Figure()
        
        # Low risk (green)
        low_risk = df[df["churn_risk"] == "Low"]["churn_probability"]
        fig.add_trace(go.Histogram(x=low_risk, name="Low Risk", marker_color="green", opacity=0.7, nbinsx=15))
        
        # Medium risk (amber)
        med_risk = df[df["churn_risk"] == "Medium"]["churn_probability"]
        fig.add_trace(go.Histogram(x=med_risk, name="Medium Risk", marker_color="orange", opacity=0.7, nbinsx=15))
        
        # High risk (red)
        high_risk = df[df["churn_risk"] == "High"]["churn_probability"]
        fig.add_trace(go.Histogram(x=high_risk, name="High Risk", marker_color="red", opacity=0.7, nbinsx=15))
        
        fig.update_layout(
            title=f"Churn Risk Distribution ({len(df)} repeat customers)",
            xaxis_title="Churn Probability",
            yaxis_title="Customer Count",
            barmode="stack",
            template="plotly_dark",
            plot_bgcolor="rgba(31, 15, 61, 0.5)",
            paper_bgcolor="rgba(15, 15, 15, 1)",
            hovermode="x unified"
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


def clv_distribution_chart(clv_output: Dict) -> go.Figure:
    """
    Box plot + bar chart showing CLV distribution
    Identifies high-value, medium-value, and low-value segments
    """
    
    try:
        if "error" in clv_output or not clv_output.get("success"):
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for CLV analysis", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        all_preds = clv_output.get("all_predictions", [])
        df = pd.DataFrame(all_preds)
        
        # Define value segments
        q1 = df["clv_estimate"].quantile(0.33)
        q2 = df["clv_estimate"].quantile(0.67)
        
        def segment_clv(clv):
            if clv >= q2:
                return "High Value"
            elif clv >= q1:
                return "Medium Value"
            else:
                return "Low Value"
        
        df["value_segment"] = df["clv_estimate"].apply(segment_clv)
        
        # Create box plot
        fig = px.box(df, 
                    x="value_segment", 
                    y="clv_estimate",
                    color="value_segment",
                    title="Customer Lifetime Value Distribution",
                    labels={"clv_estimate": "Predicted CLV (₹)", "value_segment": "Value Segment"},
                    color_discrete_map={"High Value": "green", "Medium Value": "orange", "Low Value": "red"})
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(31, 15, 61, 0.5)",
            paper_bgcolor="rgba(15, 15, 15, 1)",
            showlegend=False
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


def top_customers_table(clv_output: Dict, n_top: int = 10) -> pd.DataFrame:
    """
    Return a formatted dataframe of top customers by CLV
    """
    
    try:
        top_10 = clv_output.get("top_10_customers", [])
        df = pd.DataFrame(top_10)
        
        # Format for display
        display_df = df[[
            "customer_id", 
            "avg_transaction_value", 
            "transaction_frequency_monthly",
            "vip_affinity",
            "clv_estimate"
        ]].copy()
        
        display_df.columns = ["Customer ID", "Avg Transaction (₹)", "Visits/Month", "VIP Score", "CLV (₹)"]
        display_df["Avg Transaction (₹)"] = display_df["Avg Transaction (₹)"].round(0).astype(int)
        display_df["Visits/Month"] = display_df["Visits/Month"].round(2)
        display_df["VIP Score"] = (display_df["VIP Score"] * 100).round(0).astype(int)
        display_df["CLV (₹)"] = display_df["CLV (₹)"].round(0).astype(int)
        
        return display_df
    
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})


def ab_test_results_chart(ab_test_output: Dict) -> go.Figure:
    """
    Visualization of A/B test results with confidence intervals
    Shows control vs test group means with error bars
    """
    
    try:
        if "error" in ab_test_output:
            fig = go.Figure()
            fig.add_annotation(text="A/B test error", xref="paper", yref="paper", x=0.5, y=0.5)
            return fig
        
        # Extract data
        control_mean = ab_test_output.get("control_mean", 0)
        test_mean = ab_test_output.get("test_mean", 0)
        control_std = ab_test_output.get("control_std", 0)
        test_std = ab_test_output.get("test_std", 0)
        test_ci = ab_test_output.get("test_group_ci", [test_mean, test_mean])
        is_sig = ab_test_output.get("is_statistically_significant", False)
        
        # Create bar chart with error bars
        fig = go.Figure()
        
        # Control group
        fig.add_trace(go.Bar(
            x=["Control Group"],
            y=[control_mean],
            error_y=dict(type="data", array=[control_std], visible=True, color="lightblue"),
            marker_color="lightblue",
            name="Control",
            showlegend=True
        ))
        
        # Test group
        color = "green" if is_sig and test_mean > control_mean else ("red" if is_sig else "gray")
        fig.add_trace(go.Bar(
            x=["Test Group"],
            y=[test_mean],
            error_y=dict(type="data", array=[test_std], visible=True, color=color),
            marker_color=color,
            name="Test",
            showlegend=True
        ))
        
        # Add CI band
        if test_ci[0] != test_ci[1]:
            fig.add_shape(
                type="rect",
                x0=-0.4, x1=0.4,
                y0=test_ci[0], y1=test_ci[1],
                line=dict(color="green" if is_sig else "gray", width=2, dash="dash"),
                fillcolor="green" if is_sig else "gray",
                opacity=0.1
            )
        
        title = "A/B Test Results"
        if ab_test_output.get("percentage_difference"):
            pct = ab_test_output["percentage_difference"]
            title += f" ({pct:+.1f}%)"
        
        fig.update_layout(
            title=title,
            yaxis_title="Metric Value",
            template="plotly_dark",
            plot_bgcolor="rgba(31, 15, 61, 0.5)",
            paper_bgcolor="rgba(15, 15, 15, 1)",
            hovermode="x unified",
            height=400
        )
        
        return fig
    
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Chart error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig


def high_risk_churn_table(churn_output: Dict) -> pd.DataFrame:
    """
    Return formatted dataframe of high-risk churn customers
    """
    
    try:
        high_risk = churn_output.get("high_risk_customers", [])
        
        if len(high_risk) == 0:
            return pd.DataFrame({"Message": ["No high-risk customers detected"]})
        
        df = pd.DataFrame(high_risk)
        
        display_df = pd.DataFrame({
            "Customer ID": df["customer_id"],
            "Churn Risk": (df["churn_probability"] * 100).round(1).astype(str) + "%",
            "Risk Level": df["churn_risk"]
        })
        
        return display_df
    
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})
