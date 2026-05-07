/*=============================================================================
  E-Commerce Customer Churn Prediction — Full SAS Analysis
  DS Tools Final Project | Spring 2026
  Faculty of Computers and Data Science

  Problem: Predict which e-commerce customers will churn using behavioral,
           transactional, and demographic data. Enable proactive retention.

  Dataset: 6,200 customers | 21 raw features | 9 columns with missing values
  Target:  Churn (Yes/No) — binary classification
=============================================================================*/

/*─────────────────────────────────────────────────────────────────────────────
  CONFIGURATION & MACRO DEFINITIONS
─────────────────────────────────────────────────────────────────────────────*/
OPTIONS NODATE NONUMBER LINESIZE=120 MPRINT SYMBOLGEN;

/* === Global path macro — change this ONE place for your environment === */
%LET project_path = /home/u00000000/DS_Project;

/* === Reusable macro: Missing value summary for any dataset === */
%MACRO missing_report(dsn=, title_text=);
    TITLE "&title_text";
    PROC FORMAT;
        VALUE $missfmt ' ' = 'Missing' OTHER = 'Present';
        VALUE  missfmt .  = 'Missing' OTHER = 'Present';
    RUN;
    PROC FREQ DATA=&dsn;
        TABLES _ALL_ / MISSING NOPRINT OUT=_miss_tmp_;
    RUN;
    PROC SQL NOPRINT;
        SELECT name INTO :numvars SEPARATED BY ' '
        FROM dictionary.columns
        WHERE LIBNAME='WORK' AND MEMNAME="%UPCASE(&dsn)" AND TYPE='num';
        SELECT name INTO :charvars SEPARATED BY ' '
        FROM dictionary.columns
        WHERE LIBNAME='WORK' AND MEMNAME="%UPCASE(&dsn)" AND TYPE='char';
    QUIT;
    PROC MEANS DATA=&dsn NMISS N NOPRINT;
        VAR &numvars;
        OUTPUT OUT=_nmiss_summary_ NMISS= / AUTONAME;
    RUN;
    PROC PRINT DATA=_nmiss_summary_ NOOBS;
        TITLE2 "Numerical Variable Missing Counts";
    RUN;
%MEND missing_report;

/* === Reusable macro: Churn rate by a categorical variable === */
%MACRO churn_rate_by(dsn=, var=);
    TITLE "Churn Rate by &var";
    PROC SQL;
        SELECT &var,
               COUNT(*) AS N,
               SUM(CASE WHEN Churn='Yes' THEN 1 ELSE 0 END) AS Churned,
               CALCULATED Churned / CALCULATED N AS Churn_Rate FORMAT=PERCENT8.1
        FROM &dsn
        GROUP BY &var
        ORDER BY CALCULATED Churn_Rate DESC;
    QUIT;
%MEND churn_rate_by;

/* === Macro: Classification metrics (Precision, Recall, F1, Accuracy) === */
%MACRO classification_metrics(dsn=, actual=, predicted=, title_text=);
    TITLE "&title_text";
    PROC SQL;
        CREATE TABLE _cm_ AS
        SELECT
            SUM(CASE WHEN &actual=1 AND &predicted=1 THEN 1 ELSE 0 END) AS TP,
            SUM(CASE WHEN &actual=0 AND &predicted=0 THEN 1 ELSE 0 END) AS TN,
            SUM(CASE WHEN &actual=0 AND &predicted=1 THEN 1 ELSE 0 END) AS FP,
            SUM(CASE WHEN &actual=1 AND &predicted=0 THEN 1 ELSE 0 END) AS FN,
            COUNT(*) AS Total
        FROM &dsn;
    QUIT;
    DATA _metrics_;
        SET _cm_;
        Accuracy   = (TP + TN) / Total;
        Precision  = TP / (TP + FP);
        Recall     = TP / (TP + FN);
        F1_Score   = 2 * (Precision * Recall) / (Precision + Recall);
        Specificity = TN / (TN + FP);
        FORMAT Accuracy Precision Recall F1_Score Specificity PERCENT8.1;
    RUN;
    PROC PRINT DATA=_metrics_ NOOBS LABEL;
        VAR TP TN FP FN Total Accuracy Precision Recall F1_Score Specificity;
        LABEL TP='True Positives' TN='True Negatives' FP='False Positives'
              FN='False Negatives' Accuracy='Accuracy' Precision='Precision'
              Recall='Recall (Sensitivity)' F1_Score='F1 Score'
              Specificity='Specificity';
    RUN;
%MEND classification_metrics;

/* Output setup */
ODS HTML PATH="&project_path" (URL=NONE)
    FILE="churn_report.html" STYLE=SEASIDE;
ODS GRAPHICS ON / WIDTH=800px HEIGHT=500px IMAGEFMT=PNG;

/*=============================================================================
  STEP 1: IMPORT & UNDERSTAND THE DATA
=============================================================================*/
PROC IMPORT DATAFILE="&project_path/ecommerce_churn.csv"
    OUT=WORK.churn_raw
    DBMS=CSV
    REPLACE;
    GETNAMES=YES;
    GUESSINGROWS=6200;
RUN;

/* Custom formats for readability */
PROC FORMAT;
    VALUE churn_fmt  1 = 'Churned'  0 = 'Retained';
    VALUE sat_fmt    1 = '1-Very Low' 2 = '2-Low' 3 = '3-Medium'
                     4 = '4-High' 5 = '5-Very High';
    VALUE age_grp    LOW-25  = '18-25'   26-35 = '26-35'
                     36-45  = '36-45'   46-55 = '46-55'
                     56-HIGH = '56+';
    VALUE $contract  'Month-to-Month' = 'M2M'
                     'One Year' = '1Yr'
                     'Two Year' = '2Yr';
    VALUE risk_fmt   LOW-<0.3 = 'Low Risk'
                     0.3-<0.5 = 'Medium Risk'
                     0.5-<0.7 = 'High Risk'
                     0.7-HIGH = 'Critical';
RUN;

/* Dataset structure */
TITLE "Step 1: Dataset Structure & Metadata";
PROC CONTENTS DATA=churn_raw VARNUM;
RUN;

TITLE "Step 1: First 15 Observations";
PROC PRINT DATA=churn_raw (OBS=15) LABEL;
RUN;

/* Dataset dimensions and basic info */
TITLE "Step 1: Dataset Dimensions";
PROC SQL;
    SELECT COUNT(*) AS Total_Rows,
           (SELECT COUNT(*) FROM dictionary.columns
            WHERE LIBNAME='WORK' AND MEMNAME='CHURN_RAW') AS Total_Columns
    FROM churn_raw;
QUIT;

/*=============================================================================
  STEP 2: INVESTIGATE THE DATA — Deep Exploration
=============================================================================*/

/* 2a. Comprehensive numerical summary */
TITLE "Step 2a: Descriptive Statistics — All Numerical Variables";
PROC MEANS DATA=churn_raw N NMISS MEAN STD MIN Q1 MEDIAN Q3 MAX SKEWNESS KURTOSIS CV;
    VAR Age Tenure_Months Monthly_Charges Total_Charges
        Num_Complaints Satisfaction_Score Num_Products
        Warehouse_To_Home_KM Days_Since_Last_Order
        Cashback_Amount Coupons_Used;
RUN;

/* 2b. Detailed distribution analysis with PROC UNIVARIATE */
TITLE "Step 2b: Distribution Analysis — Tenure (Key Predictor)";
PROC UNIVARIATE DATA=churn_raw PLOTS;
    VAR Tenure_Months;
    HISTOGRAM Tenure_Months / NORMAL LOGNORMAL EXPONENTIAL
        MIDPOINTS=1 TO 72 BY 3;
    INSET N MEAN STD SKEWNESS KURTOSIS / POS=NE;
    PROBPLOT Tenure_Months / NORMAL(MU=EST SIGMA=EST);
RUN;

TITLE "Step 2b: Distribution Analysis — Monthly Charges";
PROC UNIVARIATE DATA=churn_raw;
    VAR Monthly_Charges;
    HISTOGRAM Monthly_Charges / NORMAL KERNEL;
    INSET N MEAN STD MIN MAX / POS=NE;
RUN;

TITLE "Step 2b: Distribution Analysis — Num_Complaints (Outlier Check)";
PROC UNIVARIATE DATA=churn_raw;
    VAR Num_Complaints;
    HISTOGRAM Num_Complaints / MIDPOINTS=0 TO 10 BY 1;
    INSET N MEAN STD P95 P99 MAX / POS=NE;
    /* Check for extreme outliers using IQR method */
    OUTPUT OUT=_comp_pctls_ PCTLPTS=25 75 PCTLPRE=P;
RUN;

/* 2c. Frequency analysis for categorical variables */
TITLE "Step 2c: Frequency Tables — Categorical Variables";
PROC FREQ DATA=churn_raw;
    TABLES Gender Contract Payment_Method Internet_Service
           Online_Security Tech_Support Marital_Status
           Preferred_Device Churn / NOCUM;
RUN;

/* 2d. Cross-tabulations with statistical tests */
TITLE "Step 2d: Chi-Square Test — Contract vs Churn";
PROC FREQ DATA=churn_raw;
    TABLES Contract * Churn / CHISQ EXPECTED CELLCHI2 MEASURES
        PLOTS=FREQPLOT(TWOWAY=STACKED SCALE=GROUPPCT);
RUN;

TITLE "Step 2d: Chi-Square Test — Payment Method vs Churn";
PROC FREQ DATA=churn_raw;
    TABLES Payment_Method * Churn / CHISQ MEASURES
        PLOTS=FREQPLOT(TWOWAY=STACKED SCALE=GROUPPCT);
RUN;

TITLE "Step 2d: Chi-Square Test — Internet Service vs Churn";
PROC FREQ DATA=churn_raw;
    TABLES Internet_Service * Churn / CHISQ MEASURES
        PLOTS=FREQPLOT(TWOWAY=STACKED SCALE=GROUPPCT);
RUN;

/* 2e. PROC TABULATE — Multi-dimensional summary */
TITLE "Step 2e: Average Charges & Complaints by Contract and Churn";
PROC TABULATE DATA=churn_raw FORMAT=8.2;
    CLASS Contract Churn;
    VAR Monthly_Charges Num_Complaints Satisfaction_Score Tenure_Months;
    TABLE Contract * Churn,
          Monthly_Charges*(MEAN STD)
          Num_Complaints*(MEAN)
          Satisfaction_Score*(MEAN)
          Tenure_Months*(MEAN);
RUN;

/* 2f. Two-sample T-test: Do churners have different tenure? */
TITLE "Step 2f: Two-Sample T-Test — Tenure by Churn Status";
PROC TTEST DATA=churn_raw;
    CLASS Churn;
    VAR Tenure_Months Monthly_Charges Num_Complaints;
RUN;

/* 2g. Correlation matrix */
TITLE "Step 2g: Pearson Correlation Matrix";
PROC CORR DATA=churn_raw NOSIMPLE PLOTS=MATRIX(HISTOGRAM)
    OUTP=corr_matrix;
    VAR Age Tenure_Months Monthly_Charges Total_Charges
        Num_Complaints Satisfaction_Score Days_Since_Last_Order
        Cashback_Amount Warehouse_To_Home_KM;
RUN;

/* ── VISUALIZATION 1: Churn Distribution (Bar Chart) ── */
TITLE "Visualization 1: Customer Churn Distribution";
PROC SGPLOT DATA=churn_raw;
    VBAR Churn / STAT=FREQ FILLATTRS=(COLOR=CX4C78A8)
        DATALABEL DATALABELATTRS=(SIZE=12 WEIGHT=BOLD);
    XAXIS LABEL="Churn Status" LABELATTRS=(SIZE=11);
    YAXIS LABEL="Number of Customers" LABELATTRS=(SIZE=11);
    FOOTNOTE ITALIC "~30.5% churn rate — imbalanced but workable for classification";
RUN;
FOOTNOTE;

/* ── VISUALIZATION 2: Age Distribution by Churn (Histogram + KDE) ── */
TITLE "Visualization 2: Age Distribution — Churned vs Retained";
PROC SGPANEL DATA=churn_raw;
    PANELBY Churn / LAYOUT=COLUMNLATTICE COLUMNS=2;
    HISTOGRAM Age / BINWIDTH=5 FILLATTRS=(TRANSPARENCY=0.3 COLOR=CX4C78A8);
    DENSITY Age / TYPE=KERNEL LINEATTRS=(THICKNESS=2 COLOR=CXE15759);
    COLAXIS LABEL="Customer Age";
    ROWAXIS LABEL="Frequency";
RUN;

/* ── VISUALIZATION 3: Monthly Charges by Contract & Churn (Grouped Box) ── */
TITLE "Visualization 3: Monthly Charges by Contract Type and Churn";
PROC SGPLOT DATA=churn_raw;
    VBOX Monthly_Charges / CATEGORY=Contract GROUP=Churn
        FILLATTRS=(TRANSPARENCY=0.3) MEANATTRS=(SYMBOL=DIAMONDFILLED);
    XAXIS LABEL="Contract Type";
    YAXIS LABEL="Monthly Charges ($)";
    KEYLEGEND / TITLE="Churn" LOCATION=INSIDE POSITION=TOPRIGHT;
RUN;

/* ── VISUALIZATION 4: Scatter Matrix (Multivariate) ── */
TITLE "Visualization 4: Multivariate Scatter Matrix — Key Predictors";
PROC SGSCATTER DATA=churn_raw;
    MATRIX Age Tenure_Months Monthly_Charges Num_Complaints Satisfaction_Score
        / GROUP=Churn MARKERATTRS=(SIZE=3 SYMBOL=CIRCLEFILLED)
          TRANSPARENCY=0.7 ELLIPSE=(TYPE=PREDICTION ALPHA=0.05);
RUN;

/* ── VISUALIZATION 5: Tenure Distribution by Churn (Overlaid Density) ── */
TITLE "Visualization 5: Tenure Distribution — Overlaid by Churn Status";
PROC SGPLOT DATA=churn_raw;
    DENSITY Tenure_Months / GROUP=Churn TYPE=KERNEL
        LINEATTRS=(THICKNESS=3);
    XAXIS LABEL="Tenure (Months)";
    YAXIS LABEL="Density";
    KEYLEGEND / TITLE="Churn" LOCATION=INSIDE POSITION=TOPRIGHT;
    FOOTNOTE ITALIC "Churned customers cluster heavily in the 0-15 month range";
RUN;
FOOTNOTE;

/* ── VISUALIZATION 6: Complaints vs Satisfaction (Bubble/Heat) ── */
TITLE "Visualization 6: Complaints vs Satisfaction Score by Churn";
PROC SGPLOT DATA=churn_raw;
    SCATTER X=Num_Complaints Y=Satisfaction_Score / GROUP=Churn
        MARKERATTRS=(SYMBOL=CIRCLEFILLED SIZE=6) TRANSPARENCY=0.6
        JITTER;
    XAXIS LABEL="Number of Complaints" INTEGER;
    YAXIS LABEL="Satisfaction Score (1-5)" INTEGER;
    KEYLEGEND / TITLE="Churn";
RUN;

/*=============================================================================
  STEP 3: FIX THE DATA — Handle Missing Values, Outliers, Inconsistencies
=============================================================================*/

/* 3a. Comprehensive missing value report BEFORE cleaning */
TITLE "Step 3a: Missing Value Analysis — BEFORE Cleaning";
PROC FORMAT;
    VALUE $missfmt ' ' = 'Missing' OTHER = 'Non-Missing';
    VALUE  missfmt .  = 'Missing' OTHER = 'Non-Missing';
RUN;

PROC MEANS DATA=churn_raw NMISS N MEAN STD;
    VAR Age Monthly_Charges Total_Charges Satisfaction_Score
        Warehouse_To_Home_KM Days_Since_Last_Order Cashback_Amount;
RUN;

/* Missing percentage calculation */
PROC SQL;
    TITLE2 "Missing Value Percentages";
    SELECT 'Age' AS Variable,
           SUM(CASE WHEN Age IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Monthly_Charges' AS Variable,
           SUM(CASE WHEN Monthly_Charges IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Total_Charges' AS Variable,
           SUM(CASE WHEN Total_Charges IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Satisfaction_Score' AS Variable,
           SUM(CASE WHEN Satisfaction_Score IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Warehouse_To_Home_KM' AS Variable,
           SUM(CASE WHEN Warehouse_To_Home_KM IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Days_Since_Last_Order' AS Variable,
           SUM(CASE WHEN Days_Since_Last_Order IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw
    UNION ALL
    SELECT 'Cashback_Amount' AS Variable,
           SUM(CASE WHEN Cashback_Amount IS MISSING THEN 1 ELSE 0 END) AS Missing_Count,
           CALCULATED Missing_Count / COUNT(*) AS Missing_Pct FORMAT=PERCENT8.1
    FROM churn_raw;
QUIT;

PROC FREQ DATA=churn_raw;
    TABLES Online_Security Tech_Support / MISSING;
    TITLE2 "Categorical Variable Missing Values";
RUN;

/* 3b. Outlier detection using IQR method */
TITLE "Step 3b: Outlier Detection — IQR Method";
PROC MEANS DATA=churn_raw Q1 Q3 NOPRINT;
    VAR Num_Complaints Total_Charges Warehouse_To_Home_KM;
    OUTPUT OUT=_iqr_stats_
        Q1=Q1_comp Q1_tc Q1_wh
        Q3=Q3_comp Q3_tc Q3_wh;
RUN;

DATA _null_;
    SET _iqr_stats_;
    IQR_comp = Q3_comp - Q1_comp;
    IQR_tc = Q3_tc - Q1_tc;
    IQR_wh = Q3_wh - Q1_wh;
    upper_comp_val = Q3_comp + 1.5 * IQR_comp;
    upper_tc_val   = Q3_tc   + 1.5 * IQR_tc;
    upper_wh_val   = Q3_wh   + 1.5 * IQR_wh;
    CALL SYMPUTX('upper_comp', upper_comp_val);
    CALL SYMPUTX('upper_tc',   upper_tc_val);
    CALL SYMPUTX('upper_wh',   upper_wh_val);
    PUT "Outlier Thresholds:";
    PUT "  Num_Complaints upper fence = " upper_comp_val;
    PUT "  Total_Charges upper fence  = " upper_tc_val;
    PUT "  Warehouse_KM upper fence   = " upper_wh_val;
RUN;

/* Count outliers before capping */
PROC SQL;
    TITLE2 "Outlier Counts (Beyond IQR Upper Fence)";
    SELECT
        SUM(CASE WHEN Num_Complaints > &upper_comp THEN 1 ELSE 0 END)
            AS Complaints_Outliers,
        SUM(CASE WHEN Total_Charges > &upper_tc THEN 1 ELSE 0 END)
            AS TotalCharges_Outliers,
        SUM(CASE WHEN Warehouse_To_Home_KM > &upper_wh THEN 1 ELSE 0 END)
            AS Warehouse_Outliers
    FROM churn_raw;
QUIT;

/* 3c. Impute numerical missing values with median using PROC STDIZE */
PROC STDIZE DATA=churn_raw OUT=churn_imputed
    METHOD=MEDIAN REPONLY;
    VAR Age Monthly_Charges Total_Charges Satisfaction_Score
        Warehouse_To_Home_KM Days_Since_Last_Order Cashback_Amount;
RUN;

/* 3d. Handle categorical missing, fix inconsistencies, cap outliers */
DATA churn_clean;
    SET churn_imputed;

    /* Categorical missing: impute with mode */
    IF MISSING(Online_Security) THEN Online_Security = "No";
    IF MISSING(Tech_Support) THEN Tech_Support = "No";

    /* Data entry fix: negative Total_Charges shouldn't exist */
    IF Total_Charges < 0 THEN Total_Charges = Monthly_Charges * Tenure_Months;

    /* Outlier capping using IQR-derived thresholds */
    IF Num_Complaints > &upper_comp THEN Num_Complaints = ROUND(&upper_comp);
    IF Warehouse_To_Home_KM > &upper_wh THEN Warehouse_To_Home_KM = ROUND(&upper_wh, 0.1);

    /* Business rule: Days_Since_Last_Order cannot exceed 365 */
    IF Days_Since_Last_Order > 365 THEN Days_Since_Last_Order = 365;

    /* Standardize casing for consistency */
    Gender = PROPCASE(Gender);
    Marital_Status = PROPCASE(Marital_Status);
RUN;

/* 3e. Verify cleaning: missing values AFTER */
TITLE "Step 3e: Missing Values — AFTER Cleaning (Should Be Zero)";
PROC MEANS DATA=churn_clean NMISS N;
    VAR Age Monthly_Charges Total_Charges Satisfaction_Score
        Warehouse_To_Home_KM Days_Since_Last_Order Cashback_Amount;
RUN;

PROC FREQ DATA=churn_clean;
    TABLES Online_Security Tech_Support / MISSING;
    TITLE2 "Categorical Variables After Cleaning";
RUN;

/* ── VISUALIZATION 7: Before vs After — Age (Side by Side) ── */
TITLE "Visualization 7a: Age Distribution — BEFORE Cleaning (180 Missing)";
PROC SGPLOT DATA=churn_raw;
    HISTOGRAM Age / BINWIDTH=5 FILLATTRS=(COLOR=CXE15759 TRANSPARENCY=0.3);
    DENSITY Age / TYPE=KERNEL LINEATTRS=(THICKNESS=2 COLOR=CX333333);
    XAXIS LABEL="Age" VALUES=(15 TO 85 BY 5);
    YAXIS LABEL="Frequency";
    FOOTNOTE ITALIC "180 missing values (2.9%) — gaps in distribution";
RUN;
FOOTNOTE;

TITLE "Visualization 7b: Age Distribution — AFTER Cleaning (Median Imputed)";
PROC SGPLOT DATA=churn_clean;
    HISTOGRAM Age / BINWIDTH=5 FILLATTRS=(COLOR=CX4C78A8 TRANSPARENCY=0.3);
    DENSITY Age / TYPE=KERNEL LINEATTRS=(THICKNESS=2 COLOR=CX333333);
    XAXIS LABEL="Age" VALUES=(15 TO 85 BY 5);
    YAXIS LABEL="Frequency";
    FOOTNOTE ITALIC "All missing imputed — distribution shape preserved";
RUN;
FOOTNOTE;

/* ── VISUALIZATION 8: Outlier Visualization — Complaints Box Plot ── */
TITLE "Visualization 8: Complaint Outlier Detection (Before vs After Capping)";
DATA _outlier_compare_;
    SET churn_raw (KEEP=Num_Complaints IN=A)
        churn_clean (KEEP=Num_Complaints IN=B);
    LENGTH Stage $15;
    IF A THEN Stage = "1-Before";
    IF B THEN Stage = "2-After";
RUN;

PROC SGPLOT DATA=_outlier_compare_;
    VBOX Num_Complaints / CATEGORY=Stage
        FILLATTRS=(TRANSPARENCY=0.2 COLOR=CX76B7B2)
        MEANATTRS=(SYMBOL=DIAMONDFILLED SIZE=8);
    XAXIS LABEL="Cleaning Stage";
    YAXIS LABEL="Number of Complaints";
    REFLINE &upper_comp / AXIS=Y LINEATTRS=(PATTERN=DASH COLOR=RED THICKNESS=2)
        LABEL="IQR Upper Fence";
RUN;

/*=============================================================================
  STEP 4: CREATE NEW INSIGHTS — Feature Engineering (7 New Features)
=============================================================================*/

DATA churn_features;
    SET churn_clean;

    /* ── Feature 1: Average Charge Per Month ── */
    /* WHY: Total_Charges / Tenure reveals true avg spend over the lifetime.
       Current Monthly_Charges may differ due to plan upgrades/downgrades.
       This captures spending trajectory — rising avg = upgrading customer. */
    IF Tenure_Months > 0 THEN Avg_Charge_Per_Month = Total_Charges / Tenure_Months;
    ELSE Avg_Charge_Per_Month = Monthly_Charges;

    /* ── Feature 2: Charge Deviation (current vs historical avg) ── */
    /* WHY: If current monthly charge is much higher than historical average,
       the customer may have recently upgraded and is at price shock risk.
       Negative deviation = downgrade = potential disengagement signal. */
    Charge_Deviation = Monthly_Charges - Avg_Charge_Per_Month;

    /* ── Feature 3: Tenure Group (lifecycle stage) ── */
    /* WHY: Customer behavior follows lifecycle stages. New customers churn
       due to onboarding friction; mature customers churn due to value decay.
       Each stage needs different retention strategies. */
    LENGTH Tenure_Group $12;
    IF Tenure_Months <= 6 THEN Tenure_Group = "1-New";
    ELSE IF Tenure_Months <= 18 THEN Tenure_Group = "2-Growing";
    ELSE IF Tenure_Months <= 36 THEN Tenure_Group = "3-Mature";
    ELSE IF Tenure_Months <= 54 THEN Tenure_Group = "4-Established";
    ELSE Tenure_Group = "5-Loyal";

    /* ── Feature 4: Complaint Rate (per month of tenure) ── */
    /* WHY: Raw complaint count is misleading without normalizing by tenure.
       A customer with 3 complaints in 2 months is a red flag;
       3 complaints over 5 years is normal friction. */
    IF Tenure_Months > 0 THEN Complaint_Rate = Num_Complaints / Tenure_Months;
    ELSE Complaint_Rate = Num_Complaints;

    /* ── Feature 5: Engagement Score (composite behavioral metric) ── */
    /* WHY: No single metric captures "engagement." This composite metric
       weighs satisfaction (strongest signal), product breadth (stickiness),
       recency (momentum), and deal usage (price sensitivity).
       Each component is scaled to contribute roughly equally. */
    Engagement_Score = (Satisfaction_Score * 2)  /* 2-10 range */
                     + Num_Products              /* 1-5 range  */
                     - (Days_Since_Last_Order / 30)  /* penalty for inactivity */
                     + (Coupons_Used * 0.5)      /* deal engagement bonus */
                     + (Cashback_Amount / 100);  /* reward program participation */

    /* ── Feature 6: High Value Customer Flag ── */
    /* WHY: Combines two dimensions — spending level AND loyalty duration.
       High spenders on short tenure are "new premium" (different risk).
       Long-tenure high spenders are the most valuable to retain. */
    IF Monthly_Charges > 68 AND Tenure_Months > 24 THEN High_Value = 1;
    ELSE High_Value = 0;

    /* ── Feature 7: Digital Engagement Flag ── */
    /* WHY: Digital payment + online security = customers who've invested
       in the platform's digital ecosystem. Switching costs are higher
       for digitally engaged customers — they're naturally stickier. */
    IF Payment_Method IN ("Credit Card", "Bank Transfer")
       AND Online_Security = "Yes" THEN Digital_Engaged = 1;
    ELSE Digital_Engaged = 0;

    /* ── Feature 8: Interaction — Contract x Complaints ── */
    /* WHY: The impact of complaints depends on contract type.
       A complaint from a month-to-month customer is critical (they can
       leave immediately). Same complaint from a 2-year contract customer
       is less urgent. This interaction captures that nuance. */
    IF Contract = "Month-to-Month" THEN Contract_Complaint_Risk = Num_Complaints * 2;
    ELSE IF Contract = "One Year" THEN Contract_Complaint_Risk = Num_Complaints * 1;
    ELSE Contract_Complaint_Risk = Num_Complaints * 0.5;

    /* ── Numeric target for modeling ── */
    IF Churn = "Yes" THEN Churn_Flag = 1;
    ELSE Churn_Flag = 0;
RUN;

/* Verify engineered features */
TITLE "Step 4: Engineered Features — Statistical Summary";
PROC MEANS DATA=churn_features N MEAN STD MIN MEDIAN MAX;
    VAR Avg_Charge_Per_Month Charge_Deviation Complaint_Rate
        Engagement_Score High_Value Digital_Engaged
        Contract_Complaint_Risk Churn_Flag;
RUN;

/* Do engineered features actually differ between churned/retained? */
TITLE "Step 4: T-Test — Engineered Features by Churn Status";
PROC TTEST DATA=churn_features;
    CLASS Churn;
    VAR Engagement_Score Complaint_Rate Charge_Deviation
        Contract_Complaint_Risk;
RUN;

/* ── VISUALIZATION 9: Engagement Score by Churn ── */
TITLE "Visualization 9: Engagement Score by Churn Status";
PROC SGPLOT DATA=churn_features;
    VBOX Engagement_Score / CATEGORY=Churn
        FILLATTRS=(TRANSPARENCY=0.2 COLOR=CX59A14F)
        MEANATTRS=(SYMBOL=DIAMONDFILLED SIZE=8 COLOR=RED);
    XAXIS LABEL="Churn Status";
    YAXIS LABEL="Engagement Score (Composite)";
    REFLINE 5.0 / AXIS=Y LINEATTRS=(PATTERN=DASH COLOR=RED)
        LABEL="Engagement Threshold";
RUN;

/* ── VISUALIZATION 10: Churn Rate by Tenure Lifecycle ── */
TITLE "Visualization 10: Churn Rate Across Customer Lifecycle";
PROC SGPLOT DATA=churn_features;
    VBAR Tenure_Group / GROUP=Churn GROUPDISPLAY=CLUSTER
        STAT=FREQ DATALABEL DATALABELATTRS=(SIZE=9);
    XAXIS LABEL="Customer Lifecycle Stage" DISCRETEORDER=DATA;
    YAXIS LABEL="Number of Customers";
    KEYLEGEND / TITLE="Churn" LOCATION=INSIDE POSITION=TOPRIGHT;
RUN;

/* ── VISUALIZATION 11: Contract-Complaint Risk Interaction ── */
TITLE "Visualization 11: Contract-Complaint Risk Score by Churn";
PROC SGPLOT DATA=churn_features;
    DENSITY Contract_Complaint_Risk / GROUP=Churn TYPE=KERNEL
        LINEATTRS=(THICKNESS=3);
    XAXIS LABEL="Contract-Complaint Risk Score";
    YAXIS LABEL="Density";
    KEYLEGEND / TITLE="Churn";
    FOOTNOTE ITALIC "Higher risk scores cluster among churned customers";
RUN;
FOOTNOTE;

/*=============================================================================
  STEP 5: BUILD MODELS — Logistic Regression + Decision Tree
=============================================================================*/

/* 5a. Train/Test Split (70/30, stratified by Churn_Flag) */
PROC SORT DATA=churn_features;
    BY Churn_Flag;
RUN;

PROC SURVEYSELECT DATA=churn_features OUT=churn_split
    METHOD=SRS SAMPRATE=0.7 SEED=42 OUTALL;
    STRATA Churn_Flag;
RUN;

DATA churn_train churn_test;
    SET churn_split;
    IF Selected = 1 THEN OUTPUT churn_train;
    ELSE OUTPUT churn_test;
RUN;

/* Verify stratified split preserves churn ratio */
TITLE "Step 5a: Train/Test Split — Churn Distribution Check";
PROC FREQ DATA=churn_train;
    TABLES Churn_Flag / NOCUM;
    TITLE2 "Training Set (70%)";
RUN;
PROC FREQ DATA=churn_test;
    TABLES Churn_Flag / NOCUM;
    TITLE2 "Test Set (30%)";
RUN;

/* ═══════════════════════════════════════════════════════════════════════════
   MODEL 1: LOGISTIC REGRESSION (Primary Model)
   ═══════════════════════════════════════════════════════════════════════════ */
TITLE "Step 5b: Logistic Regression — Churn Prediction (Stepwise)";
PROC LOGISTIC DATA=churn_train DESCENDING
    PLOTS(ONLY)=(ROC(ID=PROB) EFFECT ODDSRATIO INFLUENCE);
    CLASS Contract (REF="Two Year")
          Payment_Method (REF="Credit Card")
          Internet_Service (REF="None")
          Online_Security (REF="Yes")
          Tech_Support (REF="Yes")
          Tenure_Group (REF="5-Loyal")
          Gender (REF="Female")
          Marital_Status (REF="Married")
          Preferred_Device (REF="Desktop")
          / PARAM=REF;

    MODEL Churn_Flag (EVENT='1') =
        /* Original features */
        Age
        Tenure_Months
        Monthly_Charges
        Num_Complaints
        Satisfaction_Score
        Days_Since_Last_Order
        Warehouse_To_Home_KM
        Cashback_Amount
        /* Engineered features */
        Engagement_Score
        Complaint_Rate
        Charge_Deviation
        High_Value
        Digital_Engaged
        Contract_Complaint_Risk
        /* Categorical features */
        Contract
        Payment_Method
        Internet_Service
        Online_Security
        Tenure_Group
        / SELECTION=STEPWISE SLE=0.05 SLS=0.05
          LACKFIT RSQUARE STB CORRB
          CTABLE PPROB=(0.3 0.4 0.5 0.6);

    /* Score training set (for calibration check) */
    OUTPUT OUT=train_scored PREDICTED=P_Churn_Train;

    /* Score test set */
    SCORE DATA=churn_test OUT=test_scored_logistic;

    /* Store model */
    STORE churn_logistic_store;

    /* ROC curve will be auto-generated */
RUN;

/* Classify test predictions */
DATA test_scored_logistic;
    SET test_scored_logistic;
    IF P_1 >= 0.5 THEN Predicted_Churn = 1;
    ELSE Predicted_Churn = 0;
    /* Also create optimized threshold prediction */
    IF P_1 >= 0.4 THEN Predicted_Churn_Opt = 1;
    ELSE Predicted_Churn_Opt = 0;
RUN;

/* Confusion Matrix — Standard 0.5 threshold */
TITLE "Step 5c: Confusion Matrix — Logistic Regression (Threshold=0.5)";
PROC FREQ DATA=test_scored_logistic;
    TABLES Churn_Flag * Predicted_Churn / NOPERCENT NOROW NOCOL SENSPEC;
RUN;

/* Full classification metrics */
%classification_metrics(dsn=test_scored_logistic, actual=Churn_Flag,
    predicted=Predicted_Churn,
    title_text=Step 5c: Classification Metrics — Logistic (Threshold=0.5));

/* Optimized threshold metrics */
TITLE "Step 5c: Confusion Matrix — Logistic Regression (Threshold=0.4)";
PROC FREQ DATA=test_scored_logistic;
    TABLES Churn_Flag * Predicted_Churn_Opt / NOPERCENT NOROW NOCOL;
RUN;

%classification_metrics(dsn=test_scored_logistic, actual=Churn_Flag,
    predicted=Predicted_Churn_Opt,
    title_text=Step 5c: Classification Metrics — Logistic (Threshold=0.4 — Optimized for Recall));

/* ═══════════════════════════════════════════════════════════════════════════
   MODEL 2: DECISION TREE (Secondary Model for Comparison)
   ═══════════════════════════════════════════════════════════════════════════ */
TITLE "Step 5d: Decision Tree — Churn Prediction";
PROC HPSPLIT DATA=churn_train PLOTS=ALL;
    CLASS Churn_Flag Contract Payment_Method Internet_Service
          Online_Security Tech_Support Tenure_Group Gender
          Marital_Status Preferred_Device;
    MODEL Churn_Flag (EVENT='1') =
          Age Tenure_Months Monthly_Charges
          Num_Complaints Satisfaction_Score Engagement_Score
          Complaint_Rate High_Value Digital_Engaged Charge_Deviation
          Days_Since_Last_Order Cashback_Amount Contract_Complaint_Risk
          Contract Payment_Method Internet_Service
          Online_Security Tenure_Group;
    GROW ENTROPY;
    PRUNE COSTCOMPLEXITY;
    OUTPUT OUT=train_scored_tree;
    /* Generate scoring code; we apply it to test data below */
    CODE FILE="&project_path/tree_score.sas";
RUN;

/* Apply tree scoring code to test set */
DATA test_scored_tree;
    SET churn_test;
    %INCLUDE "&project_path/tree_score.sas";
RUN;

/* Classify tree predictions */
DATA test_scored_tree;
    SET test_scored_tree;
    IF P_Churn_Flag1 >= 0.5 THEN Predicted_Churn_Tree = 1;
    ELSE Predicted_Churn_Tree = 0;
RUN;

/* Tree metrics */
%classification_metrics(dsn=test_scored_tree, actual=Churn_Flag,
    predicted=Predicted_Churn_Tree,
    title_text=Step 5d: Classification Metrics — Decision Tree);

/* ═══════════════════════════════════════════════════════════════════════════
   MODEL COMPARISON
   ═══════════════════════════════════════════════════════════════════════════ */
TITLE "Step 5e: Model Comparison Summary";
PROC SQL;
    /* Logistic Regression metrics */
    SELECT 'Logistic Regression' AS Model,
        SUM(CASE WHEN Churn_Flag=Predicted_Churn THEN 1 ELSE 0 END) / COUNT(*)
            AS Accuracy FORMAT=PERCENT8.1,
        SUM(CASE WHEN Churn_Flag=1 AND Predicted_Churn=1 THEN 1 ELSE 0 END) /
            SUM(CASE WHEN Predicted_Churn=1 THEN 1 ELSE 0 END)
            AS Precision FORMAT=PERCENT8.1,
        SUM(CASE WHEN Churn_Flag=1 AND Predicted_Churn=1 THEN 1 ELSE 0 END) /
            SUM(CASE WHEN Churn_Flag=1 THEN 1 ELSE 0 END)
            AS Recall FORMAT=PERCENT8.1
    FROM test_scored_logistic
    UNION ALL
    SELECT 'Decision Tree',
        SUM(CASE WHEN Churn_Flag=Predicted_Churn_Tree THEN 1 ELSE 0 END) / COUNT(*),
        SUM(CASE WHEN Churn_Flag=1 AND Predicted_Churn_Tree=1 THEN 1 ELSE 0 END) /
            SUM(CASE WHEN Predicted_Churn_Tree=1 THEN 1 ELSE 0 END),
        SUM(CASE WHEN Churn_Flag=1 AND Predicted_Churn_Tree=1 THEN 1 ELSE 0 END) /
            SUM(CASE WHEN Churn_Flag=1 THEN 1 ELSE 0 END)
    FROM test_scored_tree;
QUIT;

/* ── VISUALIZATION 12: Predicted Probability Distribution ── */
TITLE "Visualization 12: Logistic Regression — Predicted Probability by Actual Churn";
PROC SGPANEL DATA=test_scored_logistic;
    PANELBY Churn_Flag / LAYOUT=COLUMNLATTICE COLUMNS=2
        HEADERATTRS=(SIZE=11);
    HISTOGRAM P_1 / BINWIDTH=0.05 FILLATTRS=(TRANSPARENCY=0.3 COLOR=CX4C78A8);
    DENSITY P_1 / TYPE=KERNEL LINEATTRS=(THICKNESS=2 COLOR=CXE15759);
    COLAXIS LABEL="Predicted P(Churn)";
    ROWAXIS LABEL="Frequency";
RUN;

/* ── VISUALIZATION 13: Model Calibration Plot ── */
/* Group predictions into deciles and compare predicted vs actual churn rate */
PROC RANK DATA=test_scored_logistic OUT=_calib_ GROUPS=10;
    VAR P_1;
    RANKS Decile;
RUN;

PROC MEANS DATA=_calib_ MEAN NOPRINT NWAY;
    CLASS Decile;
    VAR P_1 Churn_Flag;
    OUTPUT OUT=_calib_summary_ MEAN(P_1)=Predicted_Avg MEAN(Churn_Flag)=Actual_Avg;
RUN;

TITLE "Visualization 13: Model Calibration — Predicted vs Actual Churn Rate";
PROC SGPLOT DATA=_calib_summary_;
    SERIES X=Predicted_Avg Y=Actual_Avg /
        MARKERS MARKERATTRS=(SYMBOL=CIRCLEFILLED SIZE=10 COLOR=CX4C78A8)
        LINEATTRS=(THICKNESS=2 COLOR=CX4C78A8);
    LINEPARM X=0 Y=0 SLOPE=1 /
        LINEATTRS=(PATTERN=DASH COLOR=GRAY THICKNESS=2)
        LEGENDLABEL="Perfect Calibration";
    XAXIS LABEL="Mean Predicted Probability" VALUES=(0 TO 1 BY 0.1);
    YAXIS LABEL="Actual Churn Rate" VALUES=(0 TO 1 BY 0.1);
    KEYLEGEND / LOCATION=INSIDE POSITION=TOPLEFT;
    FOOTNOTE ITALIC "Points near the diagonal = well-calibrated model";
RUN;
FOOTNOTE;

/*=============================================================================
  STEP 6: EXPLAIN THE MODEL — Interpretation & Importance
=============================================================================*/

/* 6a. Churn rates by key segments (evidence for odds ratio interpretation) */
%churn_rate_by(dsn=churn_features, var=Contract);
%churn_rate_by(dsn=churn_features, var=Tenure_Group);
%churn_rate_by(dsn=churn_features, var=Payment_Method);
%churn_rate_by(dsn=churn_features, var=Online_Security);
%churn_rate_by(dsn=churn_features, var=Internet_Service);

/* 6b. Interaction analysis: Contract x Satisfaction */
TITLE "Step 6b: Interaction — Average Churn Rate by Contract & Satisfaction";
PROC TABULATE DATA=churn_features FORMAT=PERCENT8.1;
    CLASS Contract Satisfaction_Score;
    VAR Churn_Flag;
    TABLE Contract, Satisfaction_Score * Churn_Flag * MEAN;
RUN;

/* 6c. Linear Regression — Total Charges (required: PROC REG) */
TITLE "Step 6c: Linear Regression — Predicting Total Revenue Per Customer";
PROC REG DATA=churn_features
    PLOTS(ONLY)=(DIAGNOSTICS(STATS=ALL) FITPLOT RESIDUALBYPREDICTED
                 RSTUDENTBYPREDICTED COOKSD);
    MODEL Total_Charges = Monthly_Charges Tenure_Months Num_Products
                          Cashback_Amount Coupons_Used Engagement_Score
                          / VIF COLLIN STB CLB DWPROB;
    OUTPUT OUT=_reg_diag_ RSTUDENT=RStudent COOKD=CooksD H=Leverage
           PREDICTED=Predicted_TC RESIDUAL=Residual;
RUN;
QUIT;

/* ── VISUALIZATION 14: Feature Importance — Churn Rate Ladder ── */
/* Create a summary dataset showing churn rate by the most important segments */
PROC SQL;
    CREATE TABLE _importance_ AS
    SELECT 'M2M Contract' AS Factor, MEAN(Churn_Flag) AS Churn_Rate
        FROM churn_features WHERE Contract='Month-to-Month'
    UNION ALL
    SELECT '2Yr Contract', MEAN(Churn_Flag)
        FROM churn_features WHERE Contract='Two Year'
    UNION ALL
    SELECT 'Electronic Check', MEAN(Churn_Flag)
        FROM churn_features WHERE Payment_Method='Electronic Check'
    UNION ALL
    SELECT 'Credit Card', MEAN(Churn_Flag)
        FROM churn_features WHERE Payment_Method='Credit Card'
    UNION ALL
    SELECT 'New Customer (<6mo)', MEAN(Churn_Flag)
        FROM churn_features WHERE Tenure_Group='1-New'
    UNION ALL
    SELECT 'Loyal Customer (>54mo)', MEAN(Churn_Flag)
        FROM churn_features WHERE Tenure_Group='5-Loyal'
    UNION ALL
    SELECT 'No Online Security', MEAN(Churn_Flag)
        FROM churn_features WHERE Online_Security='No'
    UNION ALL
    SELECT 'Has Online Security', MEAN(Churn_Flag)
        FROM churn_features WHERE Online_Security='Yes'
    UNION ALL
    SELECT 'High Complaints (3+)', MEAN(Churn_Flag)
        FROM churn_features WHERE Num_Complaints >= 3
    UNION ALL
    SELECT 'Low Complaints (0-1)', MEAN(Churn_Flag)
        FROM churn_features WHERE Num_Complaints <= 1;
QUIT;

TITLE "Visualization 14: Churn Rate by Key Risk Factors";
PROC SGPLOT DATA=_importance_;
    HBAR Factor / RESPONSE=Churn_Rate
        FILLATTRS=(COLOR=CX4C78A8) DATALABEL DATALABELATTRS=(SIZE=10)
        CATEGORYORDER=RESPDESC;
    XAXIS LABEL="Churn Rate" VALUES=(0 TO 0.6 BY 0.1) GRID;
    YAXIS LABEL="Customer Segment" FITPOLICY=NONE;
    REFLINE 0.305 / AXIS=X LINEATTRS=(PATTERN=DASH COLOR=RED THICKNESS=2)
        LABEL="Overall Avg (30.5%)";
RUN;

/*=============================================================================
  STEP 7: MAKE IT USEFUL — Business Application & Recommendations
=============================================================================*/

/* 7a. Score all test customers into risk tiers */
DATA churn_tiers;
    SET test_scored_logistic;
    LENGTH Risk_Tier $12;
    IF P_1 >= 0.7 THEN Risk_Tier = "1-Critical";
    ELSE IF P_1 >= 0.5 THEN Risk_Tier = "2-High";
    ELSE IF P_1 >= 0.3 THEN Risk_Tier = "3-Medium";
    ELSE Risk_Tier = "4-Low";

    /* Recommended action per tier */
    LENGTH Recommended_Action $60;
    SELECT (Risk_Tier);
        WHEN ("1-Critical") Recommended_Action = "Immediate personal outreach + special offer";
        WHEN ("2-High")     Recommended_Action = "Targeted email campaign + loyalty discount";
        WHEN ("3-Medium")   Recommended_Action = "Engagement program + product recommendation";
        WHEN ("4-Low")      Recommended_Action = "Standard nurture flow";
    END;
RUN;

/* 7b. Top 25 highest-risk customers (actionable list for retention team) */
TITLE "Step 7b: Top 25 Highest Churn-Risk Customers — Action List";
PROC SORT DATA=churn_tiers OUT=churn_action_list;
    BY DESCENDING P_1;
RUN;

PROC PRINT DATA=churn_action_list (OBS=25) NOOBS LABEL;
    VAR CustomerID Contract Tenure_Months Monthly_Charges
        Num_Complaints Satisfaction_Score Engagement_Score
        P_1 Risk_Tier Recommended_Action;
    FORMAT P_1 PERCENT8.1;
    LABEL P_1='Churn Probability'
          Engagement_Score='Engagement'
          Recommended_Action='Action';
RUN;

/* 7c. Revenue at risk analysis */
TITLE "Step 7c: Monthly Revenue at Risk by Churn Tier";
PROC SQL;
    SELECT Risk_Tier,
           COUNT(*) AS Num_Customers,
           SUM(Monthly_Charges) AS Monthly_Revenue_At_Risk FORMAT=DOLLAR12.2,
           MEAN(Monthly_Charges) AS Avg_Charge FORMAT=DOLLAR8.2,
           MEAN(P_1) AS Avg_Churn_Prob FORMAT=PERCENT8.1,
           SUM(Monthly_Charges * P_1) AS Expected_Monthly_Loss FORMAT=DOLLAR12.2
    FROM churn_tiers
    GROUP BY Risk_Tier
    ORDER BY Risk_Tier;
QUIT;

/* 7d. ROI Simulation: What if we retain X% of critical customers? */
TITLE "Step 7d: Retention ROI Simulation";
PROC SQL;
    SELECT
        SUM(CASE WHEN Risk_Tier='1-Critical' THEN Monthly_Charges * 12 ELSE 0 END)
            AS Critical_Annual_Revenue FORMAT=DOLLAR15.2,
        CALCULATED Critical_Annual_Revenue * 0.10
            AS Saved_10pct FORMAT=DOLLAR15.2 LABEL='10% Retention Savings',
        CALCULATED Critical_Annual_Revenue * 0.20
            AS Saved_20pct FORMAT=DOLLAR15.2 LABEL='20% Retention Savings',
        CALCULATED Critical_Annual_Revenue * 0.30
            AS Saved_30pct FORMAT=DOLLAR15.2 LABEL='30% Retention Savings'
    FROM churn_tiers;
QUIT;

/* ── VISUALIZATION 15: Risk Tier Distribution ── */
TITLE "Visualization 15: Customer Distribution by Churn Risk Tier";
PROC SGPLOT DATA=churn_tiers;
    VBAR Risk_Tier / STAT=FREQ
        FILLATTRS=(COLOR=CXF28E2B) DATALABEL DATALABELATTRS=(SIZE=11 WEIGHT=BOLD);
    XAXIS LABEL="Risk Tier";
    YAXIS LABEL="Number of Customers";
RUN;

/* ── VISUALIZATION 16: Revenue at Risk Waterfall ── */
PROC SQL;
    CREATE TABLE _revenue_risk_ AS
    SELECT Risk_Tier,
           SUM(Monthly_Charges) AS Revenue FORMAT=DOLLAR12.2
    FROM churn_tiers
    GROUP BY Risk_Tier
    ORDER BY Risk_Tier;
QUIT;

TITLE "Visualization 16: Monthly Revenue at Risk by Tier";
PROC SGPLOT DATA=_revenue_risk_;
    VBAR Risk_Tier / RESPONSE=Revenue
        FILLATTRS=(COLOR=CXE15759) DATALABEL DATALABELATTRS=(SIZE=10);
    XAXIS LABEL="Churn Risk Tier";
    YAXIS LABEL="Monthly Revenue ($)" GRID;
RUN;

/*=============================================================================
  CLEANUP & EXPORT
=============================================================================*/
TITLE;
FOOTNOTE;
ODS HTML CLOSE;
ODS GRAPHICS OFF;

/* Export scored predictions */
PROC EXPORT DATA=churn_tiers
    OUTFILE="&project_path/churn_predictions.csv"
    DBMS=CSV REPLACE;
RUN;

/* Export action list */
PROC EXPORT DATA=churn_action_list (OBS=100)
    OUTFILE="&project_path/retention_action_list.csv"
    DBMS=CSV REPLACE;
RUN;

/* ═══════════════════════════════════════════════════════════════════════════
   PROJECT SUMMARY (printed to log)
   ═══════════════════════════════════════════════════════════════════════════ */
DATA _null_;
    PUT "════════════════════════════════════════════════════════════";
    PUT "  PROJECT COMPLETE: E-Commerce Customer Churn Prediction   ";
    PUT "════════════════════════════════════════════════════════════";
    PUT "  Dataset:       6,200 customers | 21 raw + 8 engineered features";
    PUT "  Models:        Logistic Regression (primary) + Decision Tree";
    PUT "  Visualizations: 16 custom plots + auto-generated model plots";
    PUT "  Outputs:       churn_report.html, churn_predictions.csv";
    PUT "                 retention_action_list.csv";
    PUT "════════════════════════════════════════════════════════════";
RUN;
