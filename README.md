# E-Commerce Customer Churn Prediction

**DS Tools Final Project | Spring 2026 | Faculty of Computers and Data Science**

---

## Overview

This project investigates customer churn in an e-commerce platform using SAS. We analyze 6,200 customer records across 21 features, engineer 8 new behavioral metrics, and build two classification models (Logistic Regression + Decision Tree) to predict which customers will leave — enabling targeted, data-driven retention strategies.

**Target Variable:** `Churn` (Yes/No) — whether a customer stopped purchasing.

---

## Project Structure

```
DS_Tools_Final_Project/
├── README.md                              # This file
├── ecommerce_churn.csv                    # Dataset (6,200 rows, 21 columns)
├── main_analysis.sas                      # Complete SAS analysis (all 7 steps)
├── Project_Report.md                      # Detailed written report
├── Churn_Prediction_Presentation.pptx     # PowerPoint slides (13 slides)
├── generate_dataset.py                    # Python script that created the dataset
└── create_presentation.py                 # Python script that created the slides
```

---

## Dataset Summary

| Property | Value |
|----------|-------|
| **Rows** | 6,200 customers |
| **Columns** | 21 raw features + 8 engineered |
| **Missing Values** | 9 columns, ~1,100 cells (1.4%) |
| **Target** | Churn: Yes (30.5%) / No (69.5%) |
| **Domain** | E-Commerce / Customer Retention |

### Feature Categories

| Category | Count | Examples |
|----------|-------|---------|
| Demographic | 4 | Age, Gender, Marital Status, Preferred Device |
| Behavioral | 5 | Complaints, Satisfaction, Days Since Order, Coupons, Products |
| Financial | 4 | Monthly Charges, Total Charges, Cashback, Contract |
| Service | 4 | Internet Service, Online Security, Tech Support, Payment |
| Spatial | 1 | Warehouse to Home (km) |
| Target | 1 | Churn (Yes/No) |

---

## How to Run

### Prerequisites
- SAS Studio (University Edition or SAS OnDemand for Academics)
- Upload `ecommerce_churn.csv` to your SAS environment

### Steps

1. **Upload the dataset:**
   - Log into SAS Studio
   - Upload `ecommerce_churn.csv` to your home directory (e.g., `/home/u12345678/DS_Project/`)

2. **Update the path:**
   - Open `main_analysis.sas`
   - Change the macro variable at the top:
     ```sas
     %LET project_path = /home/u12345678/DS_Project;
     ```

3. **Run the program:**
   - Select all code and click Run
   - Execution takes approximately 2-3 minutes

4. **View outputs:**
   - HTML report: `churn_report.html` (auto-generated in your project folder)
   - Predictions: `churn_predictions.csv`
   - Action list: `retention_action_list.csv`

---

## Analysis Pipeline (7 Steps)

### Step 1: Data Import & Understanding
- `PROC IMPORT` loads CSV data
- `PROC CONTENTS` examines metadata
- `PROC FORMAT` creates custom display formats

### Step 2: Data Investigation
- `PROC MEANS` — descriptive stats with skewness/kurtosis
- `PROC UNIVARIATE` — distribution fitting (Normal, Lognormal, Exponential)
- `PROC FREQ` — frequency tables + Chi-Square tests with Cramer's V
- `PROC TTEST` — two-sample t-tests (churned vs retained)
- `PROC CORR` — Pearson correlation matrix
- `PROC TABULATE` — multi-dimensional cross-tabulations

### Step 3: Data Cleaning
- **Missing values:** `PROC STDIZE` (median imputation for numerical), mode for categorical
- **Outliers:** IQR method (Q3 + 1.5*IQR fence), outlier counts reported before capping
- **Inconsistencies:** Negative Total_Charges recalculated, casing standardized
- **Before/After comparison:** Visual + statistical validation

### Step 4: Feature Engineering (8 new features)
| Feature | Formula | Business Rationale |
|---------|---------|-------------------|
| Avg_Charge_Per_Month | Total / Tenure | True avg vs current monthly — detects plan changes |
| Charge_Deviation | Current - Historical avg | Price shock or downgrade signal |
| Tenure_Group | 5-level binning | Customer lifecycle stage (New → Loyal) |
| Complaint_Rate | Complaints / Tenure | Normalized frustration metric |
| Engagement_Score | Composite of 5 inputs | Satisfaction + usage + recency + deals + rewards |
| High_Value | Charges>68 AND Tenure>24 | Priority retention flag |
| Digital_Engaged | Digital pay + Security | Platform investment = switching cost |
| Contract_Complaint_Risk | Interaction term | M2M complaints weighted 2x vs Two Year |

### Step 5: Model Building
- **Train/Test Split:** 70/30, stratified by Churn (PROC SURVEYSELECT + STRATA)
- **Model 1 — Logistic Regression:** PROC LOGISTIC, stepwise selection, two threshold tested (0.5 and 0.4)
- **Model 2 — Decision Tree:** PROC HPSPLIT, entropy splitting, cost-complexity pruning
- **Metrics:** Accuracy, Precision, Recall, F1 Score, Specificity (via custom SAS macro)
- **Model comparison:** Side-by-side SQL query comparing both models

### Step 6: Model Explanation
- Odds ratios from logistic regression (auto-plotted)
- Calibration plot (predicted vs actual churn by decile)
- Churn rate ladder showing top risk factors
- `PROC REG` for linear regression on Total_Charges (with VIF, Cook's D, DWPROB)

### Step 7: Business Application
- Risk tier scoring (Critical / High / Medium / Low)
- Revenue-at-risk analysis with expected monthly loss
- Top 25 highest-risk customer action list with recommended interventions
- ROI simulation: savings from 10%/20%/30% retention of critical tier

---

## SAS Procedures Used (20+)

| Category | Procedures |
|----------|------------|
| Data Management | PROC IMPORT, CONTENTS, PRINT, SORT, EXPORT, FORMAT |
| Statistics | PROC MEANS, UNIVARIATE, FREQ, CORR, TTEST, TABULATE |
| Modeling | PROC LOGISTIC, HPSPLIT, REG, SURVEYSELECT, STDIZE, RANK |
| Visualization | PROC SGPLOT, SGPANEL, SGSCATTER (16+ charts) |
| Programming | PROC SQL, DATA step, 3 custom macros, %LET, CALL SYMPUTX |

---

## Visualizations (16+)

1. Churn distribution bar chart
2. Age distribution by churn (histogram + kernel density)
3. Monthly charges by contract and churn (grouped box plot)
4. Multivariate scatter matrix with prediction ellipses
5. Tenure density overlay by churn status
6. Complaints vs satisfaction scatter (jittered, colored by churn)
7. Before/After cleaning — Age distribution (a & b)
8. Complaint outlier box plot with IQR reference line
9. Engagement score by churn (box plot with mean diamond)
10. Churn rate by tenure lifecycle stage (clustered bar)
11. Contract-complaint risk density overlay
12. Predicted probability distribution (panel by actual churn)
13. Model calibration plot (predicted vs actual by decile)
14. Churn rate ladder by risk factors (horizontal bar)
15. Risk tier customer distribution
16. Revenue at risk by tier

Plus auto-generated: ROC curve, odds ratio plot, decision tree diagram, regression diagnostics.

---

## Key Findings

- **Contract type** is the strongest churn predictor: Month-to-Month customers churn at ~45% vs ~15% for Two Year
- **Tenure** is protective: each additional month reduces churn odds by ~2-3%
- **Complaints** show dose-response: 3+ complaints doubles churn risk
- **Electronic Check** payment users churn at ~40% (highest among payment methods)
- **Engagement Score** (engineered) is statistically significant in the model (p < 0.05)
- **Contract x Complaint interaction** captures that M2M complaints are 2x more urgent

---

## Output Files (Generated After Running SAS)

| File | Description |
|------|-------------|
| `churn_report.html` | Full HTML report with all tables and visualizations |
| `churn_predictions.csv` | Model predictions with risk tiers for all test customers |
| `retention_action_list.csv` | Top 100 highest-risk customers with recommended actions |
