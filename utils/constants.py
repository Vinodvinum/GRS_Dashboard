"""
Business Rules & Constants for GRS Dashboard
Centralized configuration for thresholds, rules, and business logic
"""

# ============================================================
# QUEUE MANAGEMENT
# ============================================================
QUEUE_RISK_THRESHOLDS = {
    "LOW": 25,           # Queue < 25 minutes = Low Risk
    "MEDIUM": 45,       # Queue 25-45 minutes = Medium Risk
    "HIGH": 120,        # Queue > 45 minutes = High Risk
    "SLA_BREACH": 35    # SLA breach if queue >= 35 minutes
}

QUEUE_COLORS = {
    "LOW": "green",
    "MEDIUM": "orange",
    "HIGH": "red"
}

# ============================================================
# ANOMALY DETECTION
# ============================================================
ANOMALY_Z_THRESHOLD = 2.0  # Z-score threshold (2σ ≈ 95% confidence)
ANOMALY_SIGNIFICANCE = 0.95

# ============================================================
# PREDICTIVE FORECASTING
# ============================================================
FORECAST_CONFIDENCE_LEVEL = 0.95  # 95% confidence intervals
FORECAST_SIGMA_MULTIPLIER = 1.28  # For 95% CI (approximation)
FORECAST_DAYS_AHEAD = 7           # 7-day rolling forecast

# ============================================================
# REVENUE SIMULATION
# ============================================================
SIMULATION_WEEKDAY_UPLIFT_RANGE = (0, 30)      # 0-30% max
SIMULATION_VIP_MIX_RANGE = (0, 20)             # 0-20% max
SIMULATION_MIN_REVENUE_DELTA_THRESHOLD = 100   # Min delta to consider significant

# ============================================================
# CUSTOMER SEGMENTATION
# ============================================================
SEGMENTATION_N_CLUSTERS = 4  # Default 4 segments
SEGMENTATION_RANDOM_STATE = 42

SEGMENT_NAMES = {
    0: "Budget Shoppers",
    1: "Regular Families",
    2: "Premium Users",
    3: "Occasional Visitors"
}

# ============================================================
# CHURN PREDICTION
# ============================================================
CHURN_LOOKBACK_DAYS = 60        # Historical window for features
CHURN_PREDICTION_DAYS = 30      # Prediction horizon
CHURN_RISK_THRESHOLDS = {
    "HIGH": 0.7,      # > 70% = High churn risk
    "MEDIUM": 0.4,    # 40-70% = Medium risk
    "LOW": 0.0        # < 40% = Low risk
}
CHURN_MIN_CUSTOMERS = 10  # Minimum customers for reliable model

# ============================================================
# CUSTOMER LIFETIME VALUE (CLV)
# ============================================================
CLV_LOOKBACK_DAYS = 90
CLV_PREDICTED_LIFESPAN_MONTHS = 24  # Assume 24-month customer lifespan
CLV_REPEAT_BOOST = 1.2              # 20% boost for known repeaters
CLV_VIP_BOOST = 1.3                 # 30% boost for VIP-prone customers
CLV_RECENCY_DECAY = {
    30: 1.0,    # Active within 30 days = no decay
    60: 0.8,    # Inactive 30-60 days = 20% decay
    120: 0.5    # Inactive >60 days = 50% decay
}

# ============================================================
# A/B TESTING
# ============================================================
AB_TEST_CONFIDENCE_LEVEL = 0.95     # 95% confidence
AB_TEST_MIN_SAMPLE_SIZE = 30        # Minimum per group
AB_TEST_EFFECT_SIZES = {
    "NEGLIGIBLE": 0.2,
    "SMALL": 0.5,
    "MEDIUM": 0.8,
    "LARGE": 1.0
}

# ============================================================
# KPI CALCULATIONS
# ============================================================
KPI_PERIOD_TODAY = 1        # Days in "Today"
KPI_PERIOD_WEEK = 7         # Days in "Week"
KPI_PERIOD_MONTH = 30       # Days in "Month"

# ============================================================
# DATA QUALITY
# ============================================================
MIN_RECORDS_FOR_ANALYSIS = 100  # Minimum records to analyze
MIN_REPEAT_CUSTOMERS = 5        # Minimum repeats for cohort analysis

# ============================================================
# UI THEMING
# ============================================================
THEME_PRIMARY_COLOR = "#7C3AED"      # Purple
THEME_ACCENT_COLOR = "#FF8C42"       # Orange
THEME_SUCCESS_COLOR = "#10B981"       # Green
THEME_WARNING_COLOR = "#F59E0B"       # Amber
THEME_DANGER_COLOR = "#EF4444"        # Red
THEME_DARK_BG = "rgba(15, 15, 15, 1)"
THEME_PLOT_BG = "rgba(31, 15, 61, 0.5)"

# ============================================================
# EXPORT SETTINGS
# ============================================================
EXPORT_SNAPSHOT_DIRNAME = "reports"
EXPORT_TIMESTAMP_FORMAT = "%Y%m%d"
EXPORT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================
# DATA GENERATION
# ============================================================
GENERATOR_SEED = 42
GENERATOR_DAYS = 240  # 240 days of synthetic data
GENERATOR_TXN_PER_DAY = 27

ZONES = ["Snow Arena", "Kids Zone", "Adventure Rides", "Food Court", "Merch Store"]
TIME_SLOTS = ["10:30-12:30", "12:30-14:30", "14:30-16:30", "16:30-18:30"]
TICKET_TYPES = ["Standard", "Premium", "VIP", "Children"]
OFFER_TYPES = ["None", "Birthday", "Corporate", "Student", "Combo"]
FOOD_ITEMS = ["Burger", "Pizza", "Beverage", "Dessert", "Snacks", "Fries", "Popcorn", "Ice Cream"]

# ============================================================
# OFFER DISCOUNT LOGIC
# ============================================================
OFFER_DISCOUNTS = {
    "None": 0.0,
    "Birthday": 0.10,       # 10% off
    "Corporate": 0.12,      # 12% off
    "Student": 0.07,        # 7% off
    "Combo": 0.10            # 10% off
}

# ============================================================
# PRICE RANGES
# ============================================================
PRICE_TICKET_BASE = {
    "Standard": 500,
    "Premium": 750,
    "VIP": 1200,
    "Children": 300
}

PRICE_MERCHANDISE_RANGE = (45, 170)     # ₹45-170
PRICE_RENTAL_RANGE = (20, 110)          # ₹20-110
PRICE_FOOD_RANGE = (100, 400)           # ₹100-400

# ============================================================
# OPERATIONAL THRESHOLDS
# ============================================================
RIDE_ACTIVE_PERCENTAGE = 0.92   # 92% rides active at any time
REPEAT_CUSTOMER_PERCENTAGE = 0.30  # 30% repeat rate
CAPACITY_WARNING_THRESHOLD = 0.85  # Alert at 85% capacity
INCIDENT_AVERAGE = 0.8             # Poisson λ for incidents/day

# ============================================================
# BOOKING PIPELINE CONVERSIONS
# ============================================================
BOOKING_CONVERSION_RATES = {
    "leads_to_qualified": 0.72,      # 72% of leads qualify
    "qualified_to_proposal": 0.61,   # 61% of qualified get proposal
    "proposal_to_confirmed": 0.67    # 67% of proposals confirm
}

# Calculate total pipeline conversion
BOOKING_TOTAL_CONVERSION = 0.72 * 0.61 * 0.67  # ~29.4%

# ============================================================
# API RESPONSE CODES
# ============================================================
API_SUCCESS = 200
API_ERROR = 500
API_VALIDATION_ERROR = 400
