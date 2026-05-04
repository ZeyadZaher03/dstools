"""
Generate a realistic E-Commerce Customer Churn dataset with 6000+ rows.
Includes categorical/numerical features, missing values, and a binary target.
"""
import pandas as pd
import numpy as np

np.random.seed(42)
n = 6200

# --- Base features ---
customer_id = [f"CUST-{i:05d}" for i in range(1, n + 1)]
age = np.random.normal(42, 14, n).clip(18, 80).astype(int)
gender = np.random.choice(["Male", "Female"], n, p=[0.48, 0.52])
tenure_months = np.random.exponential(24, n).clip(1, 72).astype(int)
monthly_charges = np.round(np.random.uniform(18.0, 118.0, n), 2)
total_charges = np.round(monthly_charges * tenure_months + np.random.normal(0, 50, n), 2)
total_charges = np.clip(total_charges, 0, None)

contract = np.random.choice(
    ["Month-to-Month", "One Year", "Two Year"], n, p=[0.50, 0.30, 0.20]
)
payment_method = np.random.choice(
    ["Credit Card", "Bank Transfer", "Electronic Check", "Mailed Check"],
    n, p=[0.30, 0.25, 0.30, 0.15]
)
internet_service = np.random.choice(
    ["DSL", "Fiber Optic", "None"], n, p=[0.35, 0.45, 0.20]
)
online_security = np.random.choice(["Yes", "No", "No Internet"], n, p=[0.30, 0.50, 0.20])
tech_support = np.random.choice(["Yes", "No", "No Internet"], n, p=[0.28, 0.52, 0.20])
num_complaints = np.random.poisson(1.5, n)
satisfaction_score = np.random.choice([1, 2, 3, 4, 5], n, p=[0.08, 0.15, 0.30, 0.28, 0.19])
num_products = np.random.choice([1, 2, 3, 4, 5], n, p=[0.25, 0.30, 0.25, 0.12, 0.08])
warehouse_to_home_km = np.round(np.random.exponential(15, n).clip(1, 120), 1)
days_since_last_order = np.random.exponential(30, n).clip(0, 365).astype(int)
cashback_amount = np.round(np.random.uniform(0, 300, n), 2)
coupon_used = np.random.poisson(2, n)
marital_status = np.random.choice(["Single", "Married", "Divorced"], n, p=[0.35, 0.50, 0.15])
preferred_device = np.random.choice(["Mobile", "Desktop", "Tablet"], n, p=[0.50, 0.35, 0.15])

# --- Target: Churn (influenced by features) ---
churn_prob = (
    0.15
    + 0.25 * (contract == "Month-to-Month").astype(float)
    - 0.10 * (contract == "Two Year").astype(float)
    + 0.12 * (payment_method == "Electronic Check").astype(float)
    + 0.03 * num_complaints
    - 0.003 * tenure_months
    - 0.02 * satisfaction_score
    + 0.002 * days_since_last_order
    + 0.10 * (online_security == "No").astype(float)
    - 0.05 * (tech_support == "Yes").astype(float)
    + np.random.normal(0, 0.05, n)
)
churn_prob = np.clip(churn_prob, 0.02, 0.95)
churn = np.random.binomial(1, churn_prob).astype(str)
churn = np.where(churn == "1", "Yes", "No")

# --- Assemble DataFrame ---
df = pd.DataFrame({
    "CustomerID": customer_id,
    "Age": age,
    "Gender": gender,
    "Tenure_Months": tenure_months,
    "Monthly_Charges": monthly_charges,
    "Total_Charges": total_charges,
    "Contract": contract,
    "Payment_Method": payment_method,
    "Internet_Service": internet_service,
    "Online_Security": online_security,
    "Tech_Support": tech_support,
    "Num_Complaints": num_complaints,
    "Satisfaction_Score": satisfaction_score,
    "Num_Products": num_products,
    "Warehouse_To_Home_KM": warehouse_to_home_km,
    "Days_Since_Last_Order": days_since_last_order,
    "Cashback_Amount": cashback_amount,
    "Coupons_Used": coupon_used,
    "Marital_Status": marital_status,
    "Preferred_Device": preferred_device,
    "Churn": churn,
})

# --- Inject missing values (realistic patterns) ---
missing_indices = {
    "Age": np.random.choice(n, 180, replace=False),
    "Monthly_Charges": np.random.choice(n, 120, replace=False),
    "Total_Charges": np.random.choice(n, 200, replace=False),
    "Online_Security": np.random.choice(n, 95, replace=False),
    "Tech_Support": np.random.choice(n, 85, replace=False),
    "Satisfaction_Score": np.random.choice(n, 150, replace=False),
    "Warehouse_To_Home_KM": np.random.choice(n, 110, replace=False),
    "Days_Since_Last_Order": np.random.choice(n, 70, replace=False),
    "Cashback_Amount": np.random.choice(n, 90, replace=False),
}

for col, idx in missing_indices.items():
    df.loc[idx, col] = np.nan

print(f"Dataset shape: {df.shape}")
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nChurn distribution:\n{df['Churn'].value_counts()}")

df.to_csv("/Users/zeyadzaher/DS_Tools_Final_Project/ecommerce_churn.csv", index=False)
print("\nDataset saved to ecommerce_churn.csv")
