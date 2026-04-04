from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import cast

import streamlit as st

from components.charts import (
    anomaly_timeline,
    adult_child_split,
    booking_pipeline_funnel,
    capacity_utilization_chart,
    combo_offer_impact,
    day_wise_traffic,
    entry_time_distribution,
    food_top_items_chart,
    forecast_chart,
    marketing_offer_usage_chart,
    peak_hours_heatmap,
    queue_prediction_chart,
    revenue_stream_breakdown,
    revenue_trend,
    ticket_type_performance,
)
from components.advanced_charts import (
    customer_segment_bubble,
    churn_risk_distribution,
    clv_distribution_chart,
    ab_test_results_chart,
    top_customers_table,
    high_risk_churn_table,
)
from models.advanced_models import (
    customer_segmentation,
    churn_prediction,
    customer_lifetime_value,
    ab_testing_framework,
)
from components.insights import (
    build_executive_summary,
    customer_behavior_snapshot,
    detect_daily_anomalies,
    generate_business_insights,
    management_alerts,
    simulate_business_scenario,
)
from components.kpi_cards import compute_kpis, render_kpi_cards
from models.queue_prediction import predict_zone_queues
from models.prediction import forecast_next_7_days
from utils.helpers import (
    append_live_record,
    build_booking_pipeline,
    ensure_dataset,
    export_daily_mis_snapshot,
    filter_dataset,
    load_dataset,
)

DATA_PATH = Path("data/dataset.csv")


st.set_page_config(page_title="GRS Fantasy Park Smart MIS Dashboard", page_icon="🎢", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, #1a093d 0%, #0f0f0f 35%, #070707 100%);
            color: #f3f4f6;
        }
        .main .block-container {
            padding-top: 1.1rem;
        }
        .glass-card {
            background: linear-gradient(160deg, rgba(124, 58, 237, 0.16), rgba(255, 255, 255, 0.05));
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 16px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 14px 16px;
            margin-bottom: 8px;
        }
        .card-title {
            color: #d6bcfa;
            font-size: 0.9rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .card-value {
            margin-top: 6px;
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff;
        }
        .card-delta {
            margin-top: 6px;
            color: #a5b4fc;
            font-size: 0.88rem;
        }
        .insight-panel {
            background: rgba(124, 58, 237, 0.12);
            border: 1px solid rgba(124, 58, 237, 0.45);
            border-radius: 12px;
            padding: 10px 14px;
            margin-top: 10px;
        }
        .hero-panel {
            background: linear-gradient(100deg, rgba(124, 58, 237, 0.25), rgba(255, 140, 66, 0.15));
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 14px;
            padding: 14px 16px;
            margin: 8px 0 14px 0;
            box-shadow: 0 0 28px rgba(124, 58, 237, 0.25);
        }
        .hero-title {
            font-size: 1.06rem;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .hero-text {
            color: #d1d5db;
            font-size: 0.93rem;
            line-height: 1.4;
        }
        .ticker-wrap {
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            border: 1px solid rgba(248, 113, 113, 0.35);
            background: linear-gradient(90deg, rgba(127, 29, 29, 0.45), rgba(31, 41, 55, 0.45));
            margin: 8px 0 14px 0;
            box-shadow: 0 0 16px rgba(248, 113, 113, 0.2);
        }
        .ticker-track {
            white-space: nowrap;
            display: inline-block;
            padding: 10px 0;
            min-width: 100%;
            animation: ticker-scroll 26s linear infinite;
            font-size: 0.93rem;
            color: #fee2e2;
            font-weight: 600;
        }
        @keyframes ticker-scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data(path: Path):
    return load_dataset(path)


def main() -> None:
    ensure_dataset(DATA_PATH)

    st.title("🎢 GRS Fantasy Park Dashboard")
    st.caption("Smart MIS Dashboard v2 | Management-grade analytics with trend and predictive intelligence")

    st.sidebar.header("Filters")
    st.sidebar.markdown("Adjust views for performance tracking")

    df = get_data(DATA_PATH)

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    default_start = max(min_date, max_date - timedelta(days=45))

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    ticket_types = sorted(df["ticket_type"].dropna().astype(str).unique().tolist())
    selected_ticket_types = st.sidebar.multiselect("Ticket Type", ticket_types, default=ticket_types)

    offer_types = sorted(df["offer_type"].dropna().astype(str).unique().tolist())
    selected_offers = st.sidebar.multiselect("Offer Type", offer_types, default=offer_types)

    zones = sorted(df["zone"].dropna().astype(str).unique().tolist())
    selected_zones = st.sidebar.multiselect("Zone", zones, default=zones)

    min_rev = int(float(df["revenue"].min()))
    max_rev = int(float(df["revenue"].max()))
    revenue_range = st.sidebar.slider("Revenue Range", min_rev, max_rev, (min_rev, max_rev), step=100)

    st.sidebar.subheader("Simulation")
    if st.sidebar.button("Add Live Transaction"):
        append_live_record(DATA_PATH)
        st.cache_data.clear()
        st.rerun()

    auto_refresh = st.sidebar.toggle("Auto-refresh Simulation", value=False)
    refresh_seconds = st.sidebar.slider("Refresh Interval (sec)", min_value=10, max_value=60, value=20, step=5)

    if auto_refresh:
        append_live_record(DATA_PATH)
        st.cache_data.clear()
        st.markdown(f"<meta http-equiv='refresh' content='{refresh_seconds}'>", unsafe_allow_html=True)
        df = get_data(DATA_PATH)

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filtered_df = filter_dataset(df, start_date, end_date, selected_ticket_types)
    filtered_df = filtered_df[
        (filtered_df["offer_type"].isin(selected_offers))
        & (filtered_df["zone"].isin(selected_zones))
        & (filtered_df["revenue"].astype(float) >= float(revenue_range[0]))
        & (filtered_df["revenue"].astype(float) <= float(revenue_range[1]))
    ].copy()

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        return

    kpis = compute_kpis(filtered_df, df, start_date, end_date, selected_ticket_types)
    render_kpi_cards(kpis)

    today_mask = filtered_df["date"].dt.date == end_date
    week_mask = filtered_df["date"] >= (filtered_df["date"].max() - timedelta(days=6))
    month_mask = filtered_df["date"] >= (filtered_df["date"].max() - timedelta(days=29))

    today_df = filtered_df[today_mask]
    week_df = filtered_df[week_mask]
    month_df = filtered_df[month_mask]

    today_rev = float(today_df["revenue"].astype(float).sum())
    week_rev = float(week_df["revenue"].astype(float).sum())
    month_rev = float(month_df["revenue"].astype(float).sum())
    visitors_today = int(today_df["visitors"].sum()) if not today_df.empty else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("Today Revenue", f"Rs {today_rev:,.0f}")
    k2.metric("Week Revenue", f"Rs {week_rev:,.0f}")
    k3.metric("Month Revenue", f"Rs {month_rev:,.0f}")

    # Executive summary strip for management quick-read
    revenue_growth = float(kpis.get("revenue_growth_pct", 0.0))
    weekend_share = float(
        (filtered_df[filtered_df["date"].dt.day_name().isin(["Saturday", "Sunday"])]["visitors"].sum())
        / max(float(filtered_df["visitors"].sum()), 1.0)
        * 100.0
    )
    avg_capacity = float((filtered_df["booked_capacity"] / filtered_df["max_capacity"]).replace([float("inf")], 0).mean() * 100.0)

    rec_line = "Increase weekday promotions and student bundles to reduce weekend concentration."
    if revenue_growth < 0:
        rec_line = "Launch corrective campaign now: optimize pricing, improve offer mix, and reduce queue friction."
    elif avg_capacity > 80:
        rec_line = "Activate overflow staffing and dynamic slot controls to protect guest experience."

    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-title">📌 Executive Summary</div>
            <div class="hero-text">
                Revenue growth: <b>{revenue_growth:.1f}%</b> | Weekend visitor share: <b>{weekend_share:.1f}%</b> |
                Avg capacity utilization: <b>{avg_capacity:.1f}%</b><br/>
                Recommendation: {rec_line}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Smart dynamic signals for immediate action
    signal_cols = st.columns(3)
    if revenue_growth > 20:
        signal_cols[0].success("🔥 Strong growth trend observed. Consider scaling high-performing offers.")
    elif revenue_growth < 0:
        signal_cols[0].warning("⚠️ Revenue declining. Trigger tactical campaign and pricing correction.")
    else:
        signal_cols[0].info("Revenue stable. Use A/B testing to find next growth lever.")

    if weekend_share > 62:
        signal_cols[1].warning("⚠️ Traffic dependency on weekends is high. Build weekday demand strategy.")
    else:
        signal_cols[1].success("✅ Traffic distribution is healthy across the week.")

    if avg_capacity > 85:
        signal_cols[2].error("🚨 Overcrowding risk is elevated. Increase staff and slot controls now.")
    elif avg_capacity > 70:
        signal_cols[2].warning("⚠️ Capacity pressure rising. Monitor queue and incident trends closely.")
    else:
        signal_cols[2].success("✅ Capacity utilization is within safe operating range.")

    # Operational alert system (high-visibility business triggers)
    if visitors_today > 3000:
        st.error("🚨 High crowd alert! Consider crowd control measures immediately.")
    if revenue_growth < -10:
        st.warning("⚠️ Revenue drop detected compared to last period. Review offer mix and conversion funnel.")

    # Top insight of the day
    if weekend_share >= 60:
        top_insight = f"💡 Insight of the day: Weekend traffic drives {weekend_share:.1f}% of visitors. Weekday campaigns can unlock hidden revenue."
    elif revenue_growth > 15:
        top_insight = f"💡 Insight of the day: Revenue momentum is strong at {revenue_growth:.1f}%. Scale your best-performing offers now."
    else:
        top_insight = f"💡 Insight of the day: Capacity at {avg_capacity:.1f}% is stable. Focus on conversion efficiency to grow margin."
    st.success(top_insight)

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")

    # Live alert ticker for high-visibility operations monitoring
    incidents_today = int(today_df["incident_count"].sum()) if not today_df.empty else int(filtered_df["incident_count"].tail(50).sum())
    ticker_alerts: list[str] = []
    if revenue_growth < 0:
        ticker_alerts.append(f"⚠️ Revenue trend negative ({revenue_growth:.1f}%). Activate recovery campaign.")
    elif revenue_growth > 20:
        ticker_alerts.append(f"🔥 Revenue acceleration detected ({revenue_growth:.1f}%). Scale winning offers.")

    if weekend_share > 62:
        ticker_alerts.append(f"📌 Weekend dependency high ({weekend_share:.1f}%). Build weekday traffic demand.")

    if avg_capacity > 85:
        ticker_alerts.append(f"🚨 Capacity critical ({avg_capacity:.1f}%). Open overflow lanes and reassign staff.")

    if incidents_today >= 3:
        ticker_alerts.append(f"🛑 Incident spike: {incidents_today} incidents today. Review ride uptime and safety checks.")

    if not ticker_alerts:
        ticker_alerts.append("✅ Operations stable. No critical alerts at this moment.")

    ticker_text = "   |   ".join(ticker_alerts)
    st.markdown(
        f"""
        <div class="ticker-wrap">
            <div class="ticker-track">🚦 LIVE ALERT FEED  •  {ticker_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "Download Report (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="grs_smart_mis_report.csv",
        mime="text/csv",
    )
    if st.button("Generate Daily MIS Snapshot"):
        csv_path, txt_path = export_daily_mis_snapshot(filtered_df, Path("reports"))
        st.success(f"Snapshot exported: {csv_path} and {txt_path}")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Overview", "Revenue", "Visitors", "Operations", "Marketing", "Insights (AI)", "🚀 Advanced ML"]
    )

    with tab1:
        history, forecast = forecast_next_7_days(filtered_df)
        period = st.radio("Trend Period", ["Daily", "Weekly", "Monthly"], horizontal=True)
        st.plotly_chart(revenue_trend(filtered_df, period), use_container_width=True, key="overview_revenue_trend")
        st.plotly_chart(forecast_chart(history, forecast), use_container_width=True, key="overview_forecast")

        summary_cards = management_alerts(filtered_df)
        st.subheader("Executive Alerts")
        for line in summary_cards:
            st.markdown(f"- {line}")

        st.plotly_chart(revenue_stream_breakdown(filtered_df), use_container_width=True, key="overview_stream_breakdown")

    with tab2:
        s1, s2 = st.columns(2)
        with s1:
            st.plotly_chart(ticket_type_performance(filtered_df), use_container_width=True, key="revenue_ticket_performance")
            st.plotly_chart(combo_offer_impact(filtered_df), use_container_width=True, key="revenue_combo_impact")
        with s2:
            st.metric("Revenue", f"Rs {kpis['total_revenue']:,.0f}", f"{kpis['revenue_growth_pct']:.2f}%")
            st.metric("Avg Revenue / Visitor", f"Rs {kpis['avg_revenue_per_visitor']:,.0f}")
            stream_df = filtered_df[["ticket_revenue", "food_revenue", "merch_revenue", "rental_revenue"]].sum()
            st.write("Revenue Mix")
            st.write(
                {
                    "Tickets": f"Rs {float(stream_df['ticket_revenue']):,.0f}",
                    "Food": f"Rs {float(stream_df['food_revenue']):,.0f}",
                    "Merchandise": f"Rs {float(stream_df['merch_revenue']):,.0f}",
                    "Rentals": f"Rs {float(stream_df['rental_revenue']):,.0f}",
                }
            )

    with tab3:
        v1, v2 = st.columns(2)
        with v1:
            st.plotly_chart(adult_child_split(filtered_df), use_container_width=True, key="visitors_adult_child_split")
            st.plotly_chart(day_wise_traffic(filtered_df), use_container_width=True, key="visitors_day_traffic")
        with v2:
            st.plotly_chart(entry_time_distribution(filtered_df), use_container_width=True, key="visitors_entry_distribution")
            st.plotly_chart(peak_hours_heatmap(filtered_df), use_container_width=True, key="visitors_peak_heatmap")

    with tab4:
        st.subheader("Operations and Capacity")
        o1, o2 = st.columns(2)
        with o1:
            st.plotly_chart(capacity_utilization_chart(filtered_df), use_container_width=True, key="ops_capacity")
            st.plotly_chart(food_top_items_chart(filtered_df), use_container_width=True, key="ops_food_top_items")
        with o2:
            zone_load = (
                filtered_df.groupby("zone", as_index=False)
                .agg(visitors=("visitors", "sum"), incidents=("incident_count", "sum"))
                .sort_values("visitors", ascending=False)
            )
            st.dataframe(zone_load, use_container_width=True, hide_index=True)

            ride_state = filtered_df["ride_status"].value_counts().rename_axis("status").reset_index(name="count")
            st.dataframe(ride_state, use_container_width=True, hide_index=True)

            st.metric("Total Incidents", f"{int(filtered_df['incident_count'].sum())}")
            st.metric("Avg Staff On Duty", f"{float(filtered_df['staff_on_duty'].mean()):.1f}")

            queue_df = predict_zone_queues(filtered_df)
            st.plotly_chart(queue_prediction_chart(queue_df), use_container_width=True, key="ops_queue_prediction")
            st.dataframe(queue_df, use_container_width=True, hide_index=True)

            breach_count = int(queue_df["sla_breach"].sum()) if "sla_breach" in queue_df.columns else 0
            high_risk = int((queue_df["risk_level"] == "High").sum()) if "risk_level" in queue_df.columns else 0

            q1, q2 = st.columns(2)
            q1.metric("Queue SLA Breaches", f"{breach_count}")
            q2.metric("High Risk Zones", f"{high_risk}")

            if breach_count > 0:
                st.error("Queue SLA risk detected. Reallocate staff or open overflow lanes.")
            else:
                st.success("Queue SLA healthy across all zones.")

    with tab5:
        st.subheader("Marketing and Offer Analytics")
        m1, m2 = st.columns(2)
        with m1:
            st.plotly_chart(marketing_offer_usage_chart(filtered_df), use_container_width=True, key="mkt_offer_usage")
            st.plotly_chart(combo_offer_impact(filtered_df), use_container_width=True, key="mkt_combo_impact")
        with m2:
            offer_table = (
                filtered_df.groupby("offer_type", as_index=False)
                .agg(visitors=("visitors", "sum"), revenue=("revenue", "sum"))
                .sort_values("revenue", ascending=False)
            )
            st.dataframe(offer_table, use_container_width=True, hide_index=True)

            offer_share = float(filtered_df["is_combo"].mean() * 100)
            st.metric("Offer Usage %", f"{offer_share:.1f}%")

            best_offer = offer_table.iloc[0]["offer_type"] if not offer_table.empty else "N/A"
            st.metric("Best Performing Offer", str(best_offer))

            pipeline_df = build_booking_pipeline(filtered_df)
            st.plotly_chart(booking_pipeline_funnel(pipeline_df), use_container_width=True, key="mkt_booking_pipeline")
            st.dataframe(pipeline_df, use_container_width=True, hide_index=True)

    with tab6:
        summary = generate_business_insights(filtered_df)
        suggestions = cast(list[str], summary["suggestions"])
        history, forecast = forecast_next_7_days(filtered_df)
        exec_summary = build_executive_summary(filtered_df, forecast)
        behavior = customer_behavior_snapshot(filtered_df)

        st.subheader("Smart Business Insights")
        st.write(f"Best Performing Day: **{summary['best_day']}**")
        st.write(f"Lowest Traffic Day: **{summary['lowest_day']}**")

        st.subheader("AI Insights")
        for item in suggestions:
            st.markdown(f"- {item}")

        st.subheader("Executive Summary")
        for item in exec_summary:
            st.markdown(f"- {item}")

        b1, b2, b3 = st.columns(3)
        b1.metric("Avg Spend / Visitor", f"Rs {behavior['avg_spend']:,.0f}")
        b2.metric("Repeat Visitor Share", f"{behavior['repeat_ratio']:.1f}%")
        b3.metric("High-Value Transactions", f"{int(behavior['high_value_count'])}")

        st.subheader("Risk and Scenario")
        z_cutoff = st.slider("Anomaly Sensitivity (z-score)", 1.5, 3.5, 2.0, 0.1)
        anomalies = detect_daily_anomalies(filtered_df, z_threshold=float(z_cutoff))
        st.plotly_chart(anomaly_timeline(anomalies), use_container_width=True, key="ai_anomaly_timeline")

        flagged_count = int(anomalies["is_anomaly"].sum()) if "is_anomaly" in anomalies.columns else 0
        st.metric("Flagged Anomaly Days", f"{flagged_count}")

        if flagged_count > 0:
            st.dataframe(
                anomalies.loc[anomalies["is_anomaly"], ["date", "revenue", "visitors", "z_score"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No major anomalies detected for the selected period.")

        st.subheader("What-If Business Simulator")
        uplift = st.slider("Weekday Campaign Uplift (%)", 0, 40, 10, 1)
        vip_push = st.slider("VIP Mix Increase (%)", 0, 30, 5, 1)

        scenario = simulate_business_scenario(
            filtered_df,
            weekday_uplift_pct=float(uplift),
            vip_mix_increase_pct=float(vip_push),
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Baseline Revenue", f"Rs {scenario['baseline']:,.0f}")
        c2.metric("Simulated Revenue", f"Rs {scenario['simulated']:,.0f}")
        c3.metric("Projected Lift", f"Rs {scenario['delta']:,.0f}", f"{scenario['delta_pct']:.2f}%")

        st.markdown(
            """
            <div class="insight-panel">
                <b>Strategy Readout:</b> Use this simulator to test campaign intensity and premium mix before execution.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab7:
        st.subheader("🚀 Advanced ML Analytics")
        st.markdown("Enterprise-level customer intelligence, predictive models, and A/B testing framework")

        adv_tab1, adv_tab2, adv_tab3, adv_tab4 = st.tabs(
            ["Customer Segmentation", "Churn Risk", "Lifetime Value", "A/B Testing"]
        )

        # TAB 1: Customer Segmentation
        with adv_tab1:
            st.write("### Customer Segmentation Analysis")
            st.write("K-means clustering identifies distinct customer groups for targeted strategies")
            
            seg_results = customer_segmentation(filtered_df, n_clusters=4)
            
            if seg_results.get("success"):
                st.plotly_chart(
                    customer_segment_bubble(seg_results),
                    use_container_width=True,
                    key="adv_segmentation_bubble"
                )
                
                s1, s2, s3, s4 = st.columns(4)
                profiles = seg_results.get("segment_profiles", {})
                for idx, (seg_name, prof) in enumerate(profiles.items()):
                    col = [s1, s2, s3, s4][idx]
                    with col:
                        st.markdown(f"**{seg_name}**")
                        st.metric("Customers", f"{prof['customer_count']}")
                        st.metric("Avg Spend", f"₹{prof['avg_spend']:.0f}")
                        st.metric("Monthly Visits", f"{prof['avg_visits']:.1f}")
                        st.metric("Total Revenue", f"₹{prof['total_revenue']:,.0f}")
                
                qs = st.slider("Segmentation Quality (Silhouette Score)", 0.0, 1.0, 
                              seg_results.get("silhouette_score", 0.0), disabled=True)
                st.info(f"✅ Model Quality: {seg_results.get('silhouette_score', 0):.3f} (Higher is better)")
            else:
                st.error(f"Segmentation error: {seg_results.get('error', 'Unknown')}")

        # TAB 2: Churn Risk
        with adv_tab2:
            st.write("### Churn Risk Prediction")
            st.write("Identifies repeat customers at risk of not returning for targeted retention")
            
            churn_results = churn_prediction(filtered_df, lookback_days=60, prediction_days=30)
            
            if churn_results.get("success"):
                st.plotly_chart(
                    churn_risk_distribution(churn_results),
                    use_container_width=True,
                    key="adv_churn_distribution"
                )
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Repeat Customers", f"{churn_results.get('total_customers', 0)}")
                c2.metric("High Risk Count", f"{churn_results.get('high_risk_count', 0)}")
                c3.metric("Model Accuracy", f"{churn_results.get('model_accuracy', 0)*100:.1f}%")
                
                st.write("**High-Risk Customers (Churn Likely)**")
                high_risk_df = high_risk_churn_table(churn_results)
                st.dataframe(high_risk_df, use_container_width=True, hide_index=True)
                
                if len(high_risk_df) > 0:
                    st.warning(f"⚠️ {len(high_risk_df)} customers at high churn risk. Consider retention campaigns.")
            else:
                st.warning(churn_results.get("warning", churn_results.get("error", "Churn prediction unavailable")))

        # TAB 3: Customer Lifetime Value
        with adv_tab3:
            st.write("### Customer Lifetime Value (CLV)")
            st.write("Predicts long-term revenue value of each customer for acquisition & retention prioritization")
            
            clv_results = customer_lifetime_value(filtered_df, lookback_days=90)
            
            if clv_results.get("success"):
                st.plotly_chart(
                    clv_distribution_chart(clv_results),
                    use_container_width=True,
                    key="adv_clv_distribution"
                )
                
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Total Customers", f"{clv_results.get('total_customers', 0)}")
                k2.metric("Total Predicted CLV", f"₹{clv_results.get('total_predicted_clv', 0):,.0f}")
                k3.metric("Avg CLV per Customer", f"₹{clv_results.get('avg_clv', 0):,.0f}")
                k4.metric("High-Value Customers", f"{clv_results.get('high_value_customers', 0)}")
                
                st.write("**Top 10 Customers by CLV**")
                top_customers_df = top_customers_table(clv_results)
                st.dataframe(top_customers_df, use_container_width=True, hide_index=True)
                
                st.info(f"💡 Focus retention on {clv_results.get('high_value_customers', 0)} high-value customers to maximize ROI")
            else:
                st.error(f"CLV analysis error: {clv_results.get('error', 'Unknown')}")

        # TAB 4: A/B Testing Framework
        with adv_tab4:
            st.write("### A/B Testing Framework")
            st.write("Statistical comparison of control vs test groups (e.g., offer vs no-offer)")
            
            # Create synthetic A/B groups for demo
            df_with_offers = filtered_df[filtered_df["offer_type"] != "None"].copy()
            df_without_offers = filtered_df[filtered_df["offer_type"] == "None"].copy()
            
            if len(df_with_offers) > 10 and len(df_without_offers) > 10:
                ab_results = ab_testing_framework(df_without_offers, df_with_offers, metric="revenue", confidence_level=0.95)
                
                if ab_results.get("success"):
                    st.plotly_chart(
                        ab_test_results_chart(ab_results),
                        use_container_width=True,
                        key="adv_ab_test_results"
                    )
                    
                    a1, a2, a3 = st.columns(3)
                    a1.metric("Control Group (No Offer)", f"₹{ab_results.get('control_mean', 0):.0f}")
                    a2.metric("Test Group (With Offer)", f"₹{ab_results.get('test_mean', 0):.0f}")
                    a3.metric("Difference", f"{ab_results.get('percentage_difference', 0):+.1f}%")
                    
                    sig = ab_results.get("is_statistically_significant", False)
                    if sig:
                        st.success(f"✅ Result is STATISTICALLY SIGNIFICANT at 95% confidence (p-value: {ab_results.get('p_value', 0):.4f})")
                    else:
                        st.info(f"ℹ️ No significant difference detected (p-value: {ab_results.get('p_value', 0):.4f})")
                    
                    st.write("**Recommendation**")
                    st.markdown(ab_results.get("recommendation", "Test inconclusive"))
                    
                    st.write("**Detailed Results**")
                    st.json(ab_results.get("interpretation", {}))
                else:
                    st.error(f"A/B test error: {ab_results.get('error', 'Unknown')}")
            else:
                st.warning("Insufficient data for A/B testing. Need at least 10 transactions in each group.")
                st.info(f"Current split: {len(df_with_offers)} with offers, {len(df_without_offers)} without offers")


if __name__ == "__main__":
    main()
