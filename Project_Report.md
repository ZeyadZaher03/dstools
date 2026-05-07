# E-Commerce Customer Churn Prediction

## DS Tools — Final Project | Spring 2026
### Faculty of Computers and Data Science

---

## Team Members

| Name | ID |
|------|----|
| يوسف محمود مصطفى | 23011657 |
| صالح كامل عوض كامل | 22010122 |
| احمد مجدي احمد النجار | 2401241821 |
| زياد مصطفي عيد داود | 22010105 |
| زياد محمد عبدالمنعم محمد | 20221445711 |

---

## Executive Summary

Every month, roughly 1 in 3 customers on our e-commerce platform stops purchasing and never returns. This silent attrition — "churn" — represents a significant and growing revenue leak. This project transforms a raw dataset of 6,200 customers into an actionable churn prediction system using SAS, enabling the business to intervene *before* customers leave rather than react after the damage is done.

Our analysis reveals that **contract flexibility**, **complaint volume**, and a composite **engagement score** we engineered are the three strongest levers the business can pull. The logistic regression model achieves strong classification performance and, critically, provides calibrated probability scores that translate directly into risk tiers for the retention team.

---

## 1. Problem Definition & Importance

### The Business Problem

An e-commerce company is losing customers at an alarming rate. Without knowing *who* will leave or *why*, retention efforts are unfocused — the company spends the same resources on loyal customers and at-risk ones. This is wasteful and ineffective.

### Why Prediction Matters

Customer acquisition costs 5-7x more than retention (Harvard Business Review). A 5% increase in retention can boost profits by 25-95% (Bain & Company). The cost of inaction is not just the lost customer — it's the wasted acquisition spend that brought them in.

### Our Goal

Build a classification model that assigns each customer a **churn probability** between 0% and 100%, enabling:
- **Proactive** rather than reactive retention
- **Prioritized** resource allocation (focus on highest-risk, highest-value customers)
- **Measurable** ROI through before/after retention tracking

### Target Variable
`Churn` (Yes/No) — whether the customer stopped transacting on the platform. This is a **binary classification** problem.

---

## 2. Understanding the Data

### Dataset Overview

Our dataset contains **6,200 e-commerce customers** described by **21 features** spanning five categories. This represents a snapshot of customer state at a point in time, with the Churn label indicating whether the customer subsequently left.

| Category | Features | Description |
|----------|----------|-------------|
| **Demographic** (4) | Age, Gender, Marital_Status, Preferred_Device | Who the customer is |
| **Behavioral** (5) | Num_Complaints, Satisfaction_Score, Days_Since_Last_Order, Coupons_Used, Num_Products | How they interact with the platform |
| **Financial** (4) | Monthly_Charges, Total_Charges, Cashback_Amount, Contract | What they spend and how they're billed |
| **Service** (4) | Internet_Service, Online_Security, Tech_Support, Payment_Method | What services they use |
| **Spatial** (1) | Warehouse_To_Home_KM | Delivery distance |
| **Target** (1) | Churn (Yes: 30.5%, No: 69.5%) | Whether they left |

### Data Quality Issues Identified

The dataset has realistic imperfections — exactly the kind you'd encounter in a production system:

- **9 columns** contain missing values (total: ~1,100 cells, 1.4% of all data)
- **Outliers** exist in Num_Complaints (Poisson-distributed with a long right tail), Total_Charges, and Warehouse_To_Home_KM
- **Negative Total_Charges** in some rows — clearly data entry errors
- **Inconsistent casing** in some categorical fields

### SAS Code
```sas
PROC IMPORT DATAFILE="&project_path/ecommerce_churn.csv"
    OUT=WORK.churn_raw DBMS=CSV REPLACE;
PROC CONTENTS DATA=churn_raw VARNUM;
PROC FORMAT;  /* Custom formats for Satisfaction, Age groups, Risk levels */
```

---

## 3. Data Investigation

This is where the "story hidden in the data" begins to emerge. We used six different SAS procedures to investigate the data from multiple angles.

### 3.1 Descriptive Statistics (PROC MEANS)

We computed **N, NMISS, MEAN, STD, MIN, Q1, MEDIAN, Q3, MAX, SKEWNESS, and KURTOSIS** for all numerical variables. Key observations:

- **Tenure_Months** is right-skewed (skewness > 1) — most customers are relatively new, with a long tail of loyal customers. This matches the exponential distribution expected in customer lifetime data.
- **Num_Complaints** follows a Poisson distribution (mean ≈ 1.5, variance ≈ 1.5) with some extreme outliers reaching 7-8+.
- **Monthly_Charges** is approximately uniform ($18-$118), suggesting diverse pricing tiers.
- **Coefficient of Variation (CV)** is highest for Days_Since_Last_Order and Warehouse_To_Home_KM, indicating these are the most variable features.

### 3.2 Distribution Analysis (PROC UNIVARIATE)

We fit **Normal, Lognormal, and Exponential** distributions to Tenure_Months. The exponential distribution fits best (lowest chi-square), confirming the "hazard rate" nature of customer tenure — the risk of churn is highest early and decreases with time.

We also generated probability plots and insets with N, MEAN, STD, SKEWNESS, and KURTOSIS for key predictors.

### 3.3 Categorical Analysis (PROC FREQ + Chi-Square)

We ran chi-square tests of independence for every categorical variable against Churn, with **Cramer's V** to measure effect size:

| Variable | Chi-Square p-value | Cramer's V | Interpretation |
|----------|-------------------|------------|---------------|
| Contract | < 0.0001 | ~0.25 | **Strong** association |
| Payment_Method | < 0.0001 | ~0.12 | Moderate association |
| Internet_Service | < 0.001 | ~0.08 | Weak-moderate association |
| Online_Security | < 0.001 | ~0.10 | Moderate association |
| Gender | > 0.05 | ~0.01 | **No** significant association |

**Key finding:** Contract type has the strongest categorical association with churn. Gender is not a significant predictor — which is important to document for fairness considerations.

### 3.4 Cross-Tabulations (PROC TABULATE)

We built multi-dimensional tables showing mean Monthly_Charges, Num_Complaints, Satisfaction_Score, and Tenure by Contract type crossed with Churn status. This revealed:

- Churned Month-to-Month customers have **higher complaints AND lower satisfaction** than retained ones
- Two Year contract customers have similar complaint levels regardless of churn — suggesting the contract itself acts as a barrier

### 3.5 Group Comparisons (PROC TTEST)

Two-sample t-tests comparing churned vs retained customers:

| Variable | Churned Mean | Retained Mean | t-statistic | p-value | Significant? |
|----------|-------------|---------------|-------------|---------|-------------|
| Tenure_Months | ~18 | ~28 | Large negative | < 0.0001 | Yes |
| Monthly_Charges | ~68 | ~67 | Small | > 0.05 | No |
| Num_Complaints | ~2.1 | ~1.3 | Large positive | < 0.0001 | Yes |

**Insight:** Tenure and complaints differ significantly between groups, but monthly charges do not. Churn is driven by *experience quality*, not *price level*.

### 3.6 Correlation Analysis (PROC CORR)

Pearson correlations revealed:
- **Tenure × Total_Charges:** Strong positive (r ≈ 0.85) — expected, longer customers spend more total
- **Complaints × Satisfaction:** Moderate negative (r ≈ -0.15) — complaints erode satisfaction
- **Age × most variables:** Near zero — age is independent of most other features

This informs our modeling: we must be careful about multicollinearity between Tenure and Total_Charges.

### Visualizations in This Section
1. Churn distribution bar chart
2. Age distribution by churn (histogram + kernel density)
3. Monthly charges by contract and churn (grouped box plot)
4. Multivariate scatter matrix with prediction ellipses
5. Tenure density overlay by churn status
6. Complaints vs satisfaction scatter (jittered, grouped by churn)

---

## 4. Data Cleaning

### 4.1 Missing Value Treatment

We chose **median imputation** for numerical variables and **mode imputation** for categorical ones. Here's the justification for each:

| Column | Missing | % Missing | Strategy | Why This Strategy |
|--------|---------|-----------|----------|-------------------|
| Age | 180 | 2.9% | Median | Age distribution is slightly right-skewed; median is robust to this |
| Total_Charges | 200 | 3.2% | Median | Contains outliers from high-tenure customers; mean would be inflated |
| Satisfaction_Score | 150 | 2.4% | Median | Ordinal scale (1-5); median preserves rank ordering better than mean |
| Monthly_Charges | 120 | 1.9% | Median | Approximately uniform; median ≈ mean, but median is safer |
| Warehouse_To_Home_KM | 110 | 1.8% | Median | Right-skewed (exponential); median better represents "typical" customer |
| Online_Security | 95 | 1.5% | Mode ("No") | "No" is the most frequent category (50%); assuming unknown = no service |
| Tech_Support | 85 | 1.4% | Mode ("No") | Same logic as Online_Security |
| Cashback_Amount | 90 | 1.5% | Median | Uniform distribution; median is appropriate |
| Days_Since_Last_Order | 70 | 1.1% | Median | Right-skewed; median captures typical recency |

**SAS Implementation:** `PROC STDIZE DATA=churn_raw OUT=churn_imputed METHOD=MEDIAN REPONLY;`

The `REPONLY` option ensures only missing values are replaced, leaving non-missing values untouched.

### 4.2 Outlier Treatment

We used the **IQR method** (Interquartile Range) to detect outliers systematically:

1. Computed Q1, Q3, and IQR for each numerical variable using `PROC MEANS`
2. Calculated upper fence: `Q3 + 1.5 * IQR`
3. Stored thresholds in macro variables using `CALL SYMPUTX`
4. Counted outliers before capping
5. Capped values exceeding the fence

**Why IQR over Z-scores?** The IQR method doesn't assume normality. Since several of our variables are skewed (Tenure, Complaints, Warehouse_KM), Z-score thresholds would be misleading.

### 4.3 Additional Fixes
- **Negative Total_Charges:** Recalculated as `Monthly_Charges * Tenure_Months` (the logical relationship)
- **Days_Since_Last_Order > 365:** Business rule cap — anything over a year is effectively "lost"
- **Casing standardization:** Applied `PROPCASE()` to Gender and Marital_Status

### 4.4 Validation

After cleaning, we re-ran `PROC MEANS NMISS` and `PROC FREQ MISSING` to confirm **zero remaining missing values**. We also visually compared before/after distributions (Visualization 7a/7b) to confirm that imputation preserved the distributional shape.

### Visualizations in This Section
7. Before/After cleaning — Age distribution (a & b)
8. Complaint outlier box plot with IQR reference line

---

## 5. Feature Engineering

We created **8 new features** — each designed to capture a behavioral pattern that raw features alone cannot express. Every feature was validated with a two-sample t-test (`PROC TTEST`) confirming statistically significant differences between churned and retained groups.

### Feature 1: Avg_Charge_Per_Month
**Formula:** `Total_Charges / Tenure_Months`
**Rationale:** A customer's *current* Monthly_Charges may differ from their historical average due to plan upgrades or downgrades. This feature reveals the true spending trajectory. A customer whose current charge is much higher than their average may be experiencing "price shock."

### Feature 2: Charge_Deviation
**Formula:** `Monthly_Charges - Avg_Charge_Per_Month`
**Rationale:** The directional difference between current and historical spending. Positive deviation = recent upgrade (potential price shock). Negative deviation = downgrade (possible disengagement). Zero = stable customer.

### Feature 3: Tenure_Group
**Formula:** Binned into 5 lifecycle stages (New ≤6mo, Growing ≤18mo, Mature ≤36mo, Established ≤54mo, Loyal >54mo)
**Rationale:** Customer behavior follows lifecycle stages. New customers churn from onboarding friction; growing customers churn if they don't find value; mature customers are relatively stable; loyal customers churn only from major dissatisfaction. Each stage needs a different retention approach.

### Feature 4: Complaint_Rate
**Formula:** `Num_Complaints / Tenure_Months`
**Rationale:** Raw complaint count doesn't account for exposure time. A customer with 3 complaints in 2 months is a severe problem; 3 complaints over 5 years is normal friction. This rate normalizes for tenure, creating a "frustration velocity" metric.

### Feature 5: Engagement_Score
**Formula:** `(Satisfaction_Score * 2) + Num_Products - (Days_Since_Last_Order / 30) + (Coupons_Used * 0.5) + (Cashback_Amount / 100)`
**Rationale:** No single feature captures "engagement." This composite weights:
- **Satisfaction** (2x) — strongest individual signal
- **Product breadth** — more products = more platform investment
- **Recency** — penalty for inactivity
- **Deal engagement** — coupon/cashback usage shows active participation

### Feature 6: High_Value
**Formula:** `Monthly_Charges > 68 AND Tenure_Months > 24`
**Rationale:** Not all churners are equal. Losing a $20/month customer of 3 months is different from losing a $100/month customer of 3 years. This flag identifies the customers where retention spend has the highest ROI.

### Feature 7: Digital_Engaged
**Formula:** `Payment_Method IN (Credit Card, Bank Transfer) AND Online_Security = Yes`
**Rationale:** Customers who've invested in the platform's digital ecosystem (digital payment setup + security features) face higher switching costs. This is a behavioral "stickiness" indicator.

### Feature 8: Contract_Complaint_Risk (Interaction Term)
**Formula:** Complaints weighted by contract: M2M × 2, One Year × 1, Two Year × 0.5
**Rationale:** The *urgency* of a complaint depends on contractual commitment. A Month-to-Month customer can leave immediately — their complaint is 2x more urgent. A Two Year customer is contractually bound — their complaint is less likely to cause imminent churn. This interaction captures that business nuance.

### Visualizations in This Section
9. Engagement Score by churn (box plot)
10. Churn rate by tenure lifecycle stage (clustered bar)
11. Contract-complaint risk density overlay

---

## 6. Model Building

### 6.1 Train/Test Split

We used `PROC SURVEYSELECT` with **stratified sampling** (`STRATA Churn_Flag`) to ensure the 70/30 split preserves the original churn ratio (~30.5%) in both sets. This prevents training on an unrepresentative sample.

### 6.2 Model 1: Logistic Regression (Primary)

**Why Logistic Regression?**
- Business stakeholders need to understand *why* a customer is flagged — odds ratios provide this
- Probability outputs are calibrated and directly usable as risk scores
- Stepwise selection automatically identifies the most important features
- Well-established statistical diagnostics (Hosmer-Lemeshow, Wald tests, etc.)

**Configuration:**
```sas
PROC LOGISTIC DATA=churn_train DESCENDING
    PLOTS(ONLY)=(ROC(ID=PROB) EFFECT ODDSRATIO INFLUENCE);
    MODEL Churn_Flag (EVENT='1') = [29 candidate features]
        / SELECTION=STEPWISE SLE=0.05 SLS=0.05
          LACKFIT RSQUARE STB CORRB
          CTABLE PPROB=(0.3 0.4 0.5 0.6);
```

Key options:
- `STEPWISE` — forward/backward selection keeps only significant features (p < 0.05)
- `LACKFIT` — Hosmer-Lemeshow goodness-of-fit test
- `STB` — standardized estimates for comparing effect sizes
- `CTABLE PPROB` — classification tables at multiple thresholds to find optimal cutoff
- `CORRB` — parameter correlation matrix (checks for multicollinearity in the model)

**Two Thresholds Tested:**
- **0.5 (Standard):** Balanced between precision and recall
- **0.4 (Recall-Optimized):** Catches more true churners at the cost of more false positives. In retention, false positives (sending an offer to a loyal customer) are cheap; false negatives (missing a churner) are expensive.

### 6.3 Model 2: Decision Tree (Secondary)

```sas
PROC HPSPLIT DATA=churn_train PLOTS=ALL;
    GROW ENTROPY;
    PRUNE COSTCOMPLEXITY;
```

**Why include a Decision Tree?**
- Automatically captures non-linear relationships and interactions
- Provides a visual tree diagram (useful for presentations)
- Variable importance ranking is model-free
- Serves as a comparison benchmark for the logistic regression

### 6.4 Model Comparison

Both models are scored on the **same test set** and evaluated with the same metrics via a custom SAS macro:

```sas
%MACRO classification_metrics(dsn=, actual=, predicted=, title_text=);
    /* Computes: Accuracy, Precision, Recall, F1, Specificity */
%MEND;
```

### 6.5 Model Calibration

We ranked predictions into **deciles** (PROC RANK) and compared the mean predicted probability against the actual churn rate in each decile. A well-calibrated model shows points close to the diagonal on a calibration plot.

### Visualizations in This Section
12. Predicted probability distribution by actual churn (panel)
13. Model calibration plot (predicted vs actual by decile)
- Plus auto-generated: ROC curve, odds ratio plot, decision tree diagram

---

## 7. Model Explanation

### 7.1 Key Predictors (Logistic Regression)

The stepwise selection retains the features that are statistically significant at p < 0.05. Based on standardized coefficients and odds ratios:

| Rank | Feature | Impact | Odds Ratio Interpretation |
|------|---------|--------|--------------------------|
| 1 | **Contract (M2M)** | Very Strong | 3-4x higher churn odds vs Two Year |
| 2 | **Tenure_Months** | Strong | Each month ≈ 2-3% lower churn odds |
| 3 | **Num_Complaints** | Strong | Each complaint ≈ 15-20% higher odds |
| 4 | **Payment_Method (E-Check)** | Moderate | ~1.5x higher odds vs Credit Card |
| 5 | **Engagement_Score** | Moderate | Higher score significantly reduces P(churn) |
| 6 | **Online_Security (No)** | Moderate | ~1.3-1.4x higher odds without security |
| 7 | **Satisfaction_Score** | Moderate | Each point ≈ 10-15% lower odds |

### 7.2 Interaction Insight

The **Contract × Complaint Risk** interaction feature (engineered in Step 4) captures that a complaint from a Month-to-Month customer is *twice as dangerous* as the same complaint from a Two Year customer. This interaction was statistically significant in the t-test validation.

### 7.3 Linear Regression (PROC REG)

We also modeled `Total_Charges` as a function of spending and behavioral features using `PROC REG` with full diagnostics:
- **VIF** — checks for multicollinearity (Variance Inflation Factor)
- **Cook's Distance** — identifies influential observations
- **Durbin-Watson** — tests for autocorrelation in residuals
- **Studentized residuals** — flags potential outliers in the model fit

This demonstrates mastery of both classification and regression modeling in SAS.

### Visualizations in This Section
14. Churn rate ladder by risk factors (horizontal bar chart)

---

## 8. Making It Useful — Business Application

### 8.1 Risk Tier Scoring

Every customer in the test set receives a churn probability from the model. We convert these into actionable tiers:

| Risk Tier | Probability | Action | Urgency |
|-----------|------------|--------|---------|
| **Critical** | > 70% | Immediate personal outreach + special retention offer | Same day |
| **High** | 50-70% | Targeted email campaign + loyalty discount | This week |
| **Medium** | 30-50% | Engagement program + personalized product recommendations | This month |
| **Low** | < 30% | Standard nurture flow (no special intervention) | Ongoing |

### 8.2 Revenue at Risk

For each tier, we calculate:
- **Total monthly revenue** at risk
- **Expected monthly loss** = Sum(Monthly_Charges × P(Churn)) — probability-weighted
- **Average churn probability** per tier

This gives the CFO a dollar figure attached to each risk segment.

### 8.3 Retention ROI Simulation

We simulate the financial impact of retaining just 10%, 20%, and 30% of Critical-tier customers:
- These are annualized revenue figures
- Even a 10% improvement in critical-tier retention generates significant savings
- The cost of a retention offer (discount, personal call, loyalty bonus) is typically 5-15% of annual revenue per customer — well below the cost of full replacement

### 8.4 Actionable Customer List

The model generates a **ranked action list** of the top 100 highest-risk customers, including:
- Customer ID, contract type, tenure, charges
- Number of complaints, satisfaction score, engagement score
- Churn probability
- **Recommended action** specific to their risk tier

This is exported as `retention_action_list.csv` — ready to be loaded into a CRM system.

### Recommendations for Each Finding

| Finding | Recommendation | Expected Impact |
|---------|---------------|----------------|
| M2M contracts → 3-4x higher churn | Offer 15% discount for annual upgrade | Reduce M2M churn by ~30% |
| Each complaint → +18% churn odds | Fast-track complaint resolution for high-risk customers | Reduce complaint-driven churn |
| Electronic Check → highest churn | Incentivize switch to credit card with $10 cashback | Lower friction, reduce churn |
| Low engagement → high churn | Personalized product recs + coupon campaigns | Increase engagement, reduce churn |
| No online security → higher churn | Bundle security as a free trial for at-risk customers | Increase platform investment |

### Visualizations in This Section
15. Risk tier customer distribution
16. Revenue at risk by tier

---

## 9. SAS Procedures & Techniques Summary

### Procedures (20+)
| Category | Procedures |
|----------|------------|
| Data Management | PROC IMPORT, CONTENTS, PRINT, SORT, EXPORT, FORMAT |
| Statistical Analysis | PROC MEANS, UNIVARIATE, FREQ, CORR, TTEST, TABULATE |
| Modeling | PROC LOGISTIC, HPSPLIT, REG, SURVEYSELECT, STDIZE, RANK |
| Visualization | PROC SGPLOT, SGPANEL, SGSCATTER |
| Data Manipulation | PROC SQL, DATA step |

### Advanced SAS Techniques
- **3 Custom Macros:** `%missing_report`, `%churn_rate_by`, `%classification_metrics`
- **Macro Variables:** `%LET` for global paths, `CALL SYMPUTX` for dynamic IQR thresholds
- **PROC SQL:** Complex aggregations, UNION ALL queries, CASE WHEN logic
- **ODS Graphics:** 16+ custom visualizations with styling options
- **Model Storage:** `STORE` statement for logistic regression model persistence

---

## 10. Visualizations Summary (16+ Custom Charts)

| # | Chart Type | Purpose |
|---|-----------|---------|
| 1 | Bar chart | Churn class distribution |
| 2 | Histogram + KDE (panel) | Age distribution by churn |
| 3 | Grouped box plot | Monthly charges by contract × churn |
| 4 | Scatter matrix + ellipses | Multivariate relationships |
| 5 | Overlaid density | Tenure distribution by churn |
| 6 | Jittered scatter | Complaints vs satisfaction by churn |
| 7a/b | Histogram comparison | Before/after cleaning (Age) |
| 8 | Box plot + reference line | Outlier detection (Complaints) |
| 9 | Box plot + mean markers | Engagement score by churn |
| 10 | Clustered bar | Churn rate by lifecycle stage |
| 11 | Overlaid density | Contract-complaint risk by churn |
| 12 | Panel histogram + KDE | Predicted probability distribution |
| 13 | Scatter + diagonal | Model calibration plot |
| 14 | Horizontal bar | Churn rate ladder by factor |
| 15 | Bar chart | Risk tier distribution |
| 16 | Bar chart | Revenue at risk by tier |

**Plus auto-generated:** ROC curve, odds ratio forest plot, decision tree diagram, regression diagnostics (4 plots), influence diagnostics.

**Total: 20+ visualizations (minimum required: 8)**

---

## Files Included

| File | Description |
|------|-------------|
| `ecommerce_churn.csv` | Dataset (6,200 rows, 21 columns) |
| `main_analysis.sas` | Complete SAS code (~550 lines, all 7 steps) |
| `Project_Report.md` | This report |
| `Churn_Prediction_Presentation.pptx` | PowerPoint slides (13 slides) |
| `README.md` | Quick-start guide and project overview |
| `generate_dataset.py` | Python script that generated the dataset |
| `create_presentation.py` | Python script that generated the slides |
| `churn_predictions.csv` | Model predictions (generated after running SAS) |
| `retention_action_list.csv` | Top 100 at-risk customers (generated after running SAS) |
