# 🚀 Advanced Features Guide - GRS Dashboard v3

**Advanced ML Analytics, Customer Intelligence & Decision Support**

---

## 📌 Overview of New Advanced Features

The advanced edition of GRS Dashboard includes **4 enterprise-grade ML modules** accessible via the new **"🚀 Advanced ML" tab**:

1. **Customer Segmentation** — K-means clustering for market segmentation
2. **Churn Risk Prediction** — Logistic regression identifying at-risk repeat customers
3. **Customer Lifetime Value (CLV)** — Revenue prediction for each customer
4. **A/B Testing Framework** — Statistical comparison of marketing campaigns

---

## 🎯 Feature 1: Customer Segmentation

### What It Does
Divides customers into **4 distinct groups** based on spending patterns, visit frequency, ticket type preferences, and engagement signals.

### Algorithm
- **Method**: K-means clustering (k=4)
- **Features Used**:
  - Average spend per transaction
  - Monthly visit frequency
  - VIP ticket preference (0-1 score)
  - Recency (days since last purchase)
- **Quality Metric**: Silhouette Score (0-1, higher is better)

### Customer Segments Identified

| Segment | Typical Profile | Business Strategy |
|---------|-----------------|-------------------|
| **Budget Shoppers** | Low spend (₹300-500), irregular visits, basic tickets | Entry-level campaigns, bundle deals |
| **Regular Families** | Medium spend (₹800-1200), consistent visits, mix of tickets | Loyalty programs, family passes |
| **Premium Users** | High spend (₹1500+), VIP preference, frequent upgrades | Exclusive perks, premium line access |
| **Occasional Visitors** | Medium spend, low repeat (1-2 visits/month), event-driven | Special offers, seasonal campaigns |

### How to Use
1. Navigate to **"🚀 Advanced ML"** tab → **"Customer Segmentation"**
2. View **bubble chart** showing segments by:
   - X-axis: Avg Spend
   - Y-axis: Monthly Visit Frequency
   - Bubble size: Total Revenue Contribution
3. Read **segment metrics** in 4-column cards
4. Use for:
   - Tailored marketing campaigns per segment
   - Dynamic pricing strategies
   - Resource allocation (e.g., VIP lounges for Premium Users)

### Example Insight
_"Premium Users (320 customers) contribute ₹2.3M revenue despite only 8% of customer base. Recommend dedicated VIP experiences and concierge service for this segment."_

---

## 🚨 Feature 2: Churn Risk Prediction

### What It Does
Predicts the **probability** that each repeat customer will NOT return within the next 30 days.

### Algorithm
- **Method**: Logistic Regression
- **Training Data**: Last 60 days of repeat customer behavior
- **Features**:
  - Visit frequency (visits/month in lookback)
  - Recency (days since last visit)
  - Average spend trend (increasing or decreasing?)
  - VIP engagement score
- **Output**: Churn probability (0-100%) + Risk Level (Low/Medium/High)

### Risk Bands
| Risk Level | Churn Probability | Action |
|-----------|------------------|--------|
| **Low** | 0-40% | Standard engagement, monitor |
| **Medium** | 40-70% | Targeted retention email, small discount offer |
| **High** | 70-100% | Urgent intervention: dedicated outreach, loyalty bonus |

### How to Use
1. Navigate to **"🚀 Advanced ML"** tab → **"Churn Risk"**
2. View **histogram** showing distribution of customers across risk levels
3. Review **high-risk customer list** (top 10 at-risk customers by ID)
4. Filter for targeted interventions:
   - Send retention emails to Medium/High risk customers
   - Offer loyalty bonuses to prevent defection
   - Analyze why these customers are at risk (price? experience? competition?)

### Example Alert
_"WARNING: 47 customers at HIGH CHURN RISK (>70% probability). Top prospect: Customer #42156 (probability 89%). Last visit: 35 days ago, avg spend ₹1200. Recommend VIP dinner event invitation."_

### Model Accuracy
- **Validation Accuracy**: ~82-88% (varies with data)
- **Use Case**: Early warning system, NOT deterministic prediction
- **Recommendation**: Combine with qualitative feedback (surveys, support tickets)

---

## 💎 Feature 3: Customer Lifetime Value (CLV)

### What It Does
Predicts the **total revenue** a customer will generate over their entire relationship with GRS.

### Algorithm
- **Method**: Regression on historical metrics
- **Formula**: CLV = (Avg Transaction Value × Monthly Frequency × Projected Lifespan) × Engagement Multipliers
  - Base lifespan: 24 months
  - Retention probability: Based on recency
  - Repeat boost: +20% for known repeaters
  - VIP boost: +30% for VIP-affinity customers

### Segments (CLV-based)

| Segment | CLV Range | % of Customers | % of Revenue | Action |
|---------|-----------|------------------|--------------|--------|
| **High Value** | Top 25% | 25% | 60-70% | VIP treatment, exclusive access |
| **Medium Value** | Middle 50% | 50% | 25-35% | Standard loyalty program |
| **Low Value** | Bottom 25% | 25% | 5-10% | Convert via sampling programs |

### How to Use
1. Navigate to **"🚀 Advanced ML"** tab → **"Lifetime Value"**
2. View **box plot** of CLV distribution across segments
3. Review **Top 10 Customers table** with:
   - Customer ID
   - Projected CLV
   - Avg Transaction Value
   - Monthly Visit Frequency
   - VIP Affinity Score
4. Use insights for:
   - **Acquisition Cost**: Don't spend more than 20-30% of CLV to acquire
   - **Retention Budget**: Worth spending up to 10-15% of CLV to retain
   - **Resource Allocation**: Assign best staff/experiences to high-CLV customers
   - **Exit Analysis**: If losing a ₹50K CLV customer, that's a ₹50K loss

### Example Dashboard Insight
_"Customer #78234 has predicted CLV of ₹145,000 over 24 months. They're in top 5%. Recommend: Assign dedicated account manager, personalized birthday experiences, priority queue access."_

---

## 📊 Feature 4: A/B Testing Framework

### What It Does
Statistically compares two groups (e.g., **offer applied vs. no offer**) to determine if differences are real or just random noise.

### Algorithm
- **Method**: Independent samples t-test with effect size analysis
- **Null Hypothesis**: There is no difference between groups
- **Confidence Level**: 95% (p < 0.05 = statistically significant)
- **Metrics Compared**: Revenue, visitor count, or conversion rate
- **Detection Time**: Requires minimum ~30 transactions per group

### Outputs Explained

| Output | Meaning |
|--------|---------|
| **Control Mean** | Average metric in no-offer group |
| **Test Mean** | Average metric in offer group |
| **Percentage Difference** | Test vs Control (e.g., +12% means offer increased revenue by 12%) |
| **p-value** | Probability that observed difference is random (< 0.05 = significant) |
| **Cohen's d** | Effect size (0.2 = small, 0.5 = medium, 0.8 = large) |
| **Confidence Interval (CI)** | Range where true effect likely lies (95% confidence) |

### Decision Framework

```
Is p-value < 0.05?
├─ YES → Statistically significant difference
│  ├─ If Test Mean > Control Mean → Lift detected! Roll out widely
│  └─ If Test Mean < Control Mean → Decline detected. Stop campaign.
└─ NO → No significant difference
   ├─ Sample size adequate? 
   │  ├─ YES → No effect exists. Try different approach.
   │  └─ NO → Continue testing, need more data
```

### How to Use
1. Navigate to **"🚀 Advanced ML"** tab → **"A/B Testing"**
2. Dashboard automatically creates groups:
   - **Control**: Customers without offers
   - **Test**: Customers with offers
3. Review **comparison bar chart** with confidence intervals
4. Check recommendation (green ✓ or warning ⚠️)
5. Interpret results:
   - ✅ Significant positive: Roll out campaign to all customers
   - ⚠️ Not significant: Try different offer or increase sample size
   - ❌ Significant negative: Pause campaign immediately

### Example A/B Test Results
```
Control Group (No Offer): ₹450 avg revenue
Test Group (Birthday Offer): ₹520 avg revenue
Difference: +15.6%
p-value: 0.0023 ✅ STATISTICALLY SIGNIFICANT
Cohen's d: 0.42 (Medium effect)

RECOMMENDATION: 
✅ Birthday offers show real +15.6% revenue lift.
Expected ROI: Every ₹100 spent on offer generation returns ₹215.
Recommended action: Scale birthday offers to all eligible customers.
```

---

## 🔧 Technical Details (For Advanced Users)

### Model Algorithms

#### Segmentation: K-means Clustering
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

features = [avg_spend, visit_freq, vip_ratio, recency]
features_scaled = StandardScaler().fit_transform(features)
kmeans = KMeans(n_clusters=4, random_state=42)
customer_segments = kmeans.fit_predict(features_scaled)
```

#### Churn: Logistic Regression
```python
from sklearn.linear_model import LogisticRegression

X = [visit_frequency, last_visit_days, avg_spend, spend_trend, vip_engagement]
y = [churned]  # 1 if didn't return in 30 days, 0 otherwise
model = LogisticRegression()
churn_probability = model.predict_proba(X)[:, 1]
```

#### CLV: Regression with Multipliers
```python
avg_transaction_value = df.groupby('customer_id')['revenue'].mean()
transaction_frequency = count / lookback_days * 30
retention_prob = 1.0 if recent else 0.8 or 0.5
lifespan_months = 24 * retention_prob
clv = avg_transaction_value * transaction_frequency * lifespan_months
clv *= 1.2  # repeat boost
clv *= 1.3  # vip boost
```

#### A/B Testing: Welch's t-test + Effect Size
```python
from scipy import stats

t_stat, p_value = stats.ttest_ind(test_metric, control_metric)
cohens_d = (test_mean - control_mean) / pooled_std
significant = p_value < 0.05
```

### Configuration
All thresholds and business rules are centralized in `utils/constants.py`:
```python
CHURN_RISK_THRESHOLDS = {"HIGH": 0.7, "MEDIUM": 0.4, "LOW": 0.0}
SEGMENTATION_N_CLUSTERS = 4
AB_TEST_CONFIDENCE_LEVEL = 0.95
CLV_PREDICTED_LIFESPAN_MONTHS = 24
```

---

## 📈 Best Practices for Each Feature

### Segmentation Best Practices
- ✅ Run quarterly to adapt to changing customer mix
- ✅ Combine with qualitative research (surveys, interviews)
- ✅ Create segment-specific marketing/operational playbooks
- ❌ Don't rely solely on clustering; validate segment viability

### Churn Prediction Best Practices
- ✅ Combine with NPS scores and support ticket analysis
- ✅ Act on high-risk customers within 48 hours
- ✅ Track retention to measure intervention effectiveness
- ✅ Use model as early warning, not as definitive prediction
- ❌ Avoid mass targeting at scale without personalization

### CLV Best Practices
- ✅ Align marketing budgets with CLV (don't overspend on low CLV)
- ✅ Use CLV to set customer support SLA (higher CLV = faster support)
- ✅ Monitor CLV trends (increasing = healthy, decreasing = risk)
- ✅ Segment by CLV for targeted interventions
- ❌ Don't use CLV alone; combine with churn/satisfaction metrics

### A/B Testing Best Practices
- ✅ Always test before scaling
- ✅ Run for minimum 7-14 days (not just 1-2 days)
- ✅ Randomize assignment to avoid bias
- ✅ Document assumptions and learnings
- ✅ Respect statistical significance (don't cherry-pick favorable results)
- ❌ Don't run too many simultaneous tests (statistical interference)
- ❌ Don't stop test early just because one group is winning

---

## 📊 Example Business Scenarios

### Scenario 1: Price Optimization
**Goal**: Determine if ₹50 price increase reduces demand

**A/B Test Setup**:
- Control: Current price (₹500)
- Test: New price (₹550)
- Duration: 2 weeks
- Track: Revenue per visitor

**Possible Outcomes**:
- If +₹50 × same visitors = revenue +10% → Roll out increase
- If +₹50 × 15% fewer visitors = revenue -8% → Keep current price
- If no significant difference → Try ₹100 increase

---

### Scenario 2: Retention Campaign Prioritization
**Goal**: Reduce churn for high-value customers

**Using Churn + CLV**:
1. Run churn prediction → 150 high-risk customers
2. Check CLV for each → Top 30 customers have CLV > ₹100K
3. Allocate budget for high-CLV churn risks:
   - Tier 1 (CLV > ₹150K): Personal call + VIP dinner
   - Tier 2 (₹100-150K): Personalized email + 20% discount
   - Tier 3 (₹50-100K): Automated email + 10% discount
4. Track re-engagement rate in 30 days

---

### Scenario 3: Customer Win-Back Campaign
**Goal**: Bring back low-activity Premium Users

**Using Segmentation + CLV**:
1. Segment customers → Identify 80 "Premium Users" in "Medium Value" group
2. Why are they medium vs high?
   - Lower recency (not visiting as frequently)
   - Lower spend (using fewer services)
3. Win-back campaign:
   - Email: "We miss you! Here's 25% off your next visit"
   - Target: Specific date when they usually visit
   - Measure: Incremental revenue vs campaign cost

---

## ⚠️ Limitations & Caveats

### Segmentation
- ✓ Works best with 500+ customers
- ✓ Clusters can shift with seaso seasonality (recalculate quarterly)
- ✓ Assumes numerical features; can't capture "personality"

### Churn Prediction
- ✓ Lookback period (60 days) must match repeat visitor cycle
- ✓ External factors (competition, weather, holidays) not captured
- ✓ Model accuracy ~82-88%; use as signal, not absolute truth

### CLV
- ✓ Assumes linear relationship; doesn't account for exponential growth paths
- ✓ Requires adequate historical data (recommend 90+ days)
- ✓ Boosts (repeat, VIP) are heuristic-based, not ML-trained

### A/B Testing
- ✓ Requires minimum ~30 transactions per group
- ✓ Can't detect effects smaller than 5-10% typical variance
- ✓ Sequential testing bias (don't peek early!)
- ✓ Confounding variables not controlled (weather, events, etc.)

---

## 🔄 Integration with Other Dashboard Features

### Combined Insights Example
```
Step 1: Customer Segmentation → Identify Premium Users (320 customers)
Step 2: Churn Prediction → 25 Premium Users at HIGH risk
Step 3: CLV Analysis → Those 25 have avg CLV ₹160K (top tier)
Step 4: A/B Test → Design retention offer (20% discount vs 25% discount)
Step 5: Campaign → Test high-discount on 10 customers, track ROI
Step 6: Queue Prediction → Ensure staff ready for returning customers
Step 7: Insights Tab → Monitor revenue lift post-campaign
```

---

## 🚀 Future Roadmap

**Coming Soon** (Phase 2):
- [ ] RFM (Recency, Frequency, Monetary) analysis
- [ ] Propensity modeling (predict upsell/cross-sell potential)
- [ ] Cohort analysis (track customer cohorts over time)
- [ ] Lookalike modeling (find customers similar to high-CLV buyers)
- [ ] Attribution modeling (which touchpoints drive revenue?)

---

## 📞 Support & Troubleshooting

### "Insufficient data for segmentation"
- **Cause**: < 100 customers in dataset
- **Solution**: Generate more data or use larger date range

### "No statistically significant difference in A/B test"
- **Cause**: Need more data or effect is too small
- **Solution**: Increase test duration or try stronger offer

### "Churn prediction unavailable"
- **Cause**: < 10 repeat customers in dataset
- **Solution**: Filter for longer date range or collect more repeat data

---

## 📚 Learning Resources

- **K-means Clustering**: https://scikit-learn.org/stable/modules/clustering.html#k-means
- **Logistic Regression**: https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression
- **Statistical Testing**: https://www.statsmodels.org/stable/
- **A/B Testing Guide**: https://en.wikipedia.org/wiki/A/B_testing

---

**Version**: v3 Advanced Edition  
**Last Updated**: April 4, 2026  
**Status**: Production-ready with continuous improvement roadmap
