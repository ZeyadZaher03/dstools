"""
Merge SAS prediction outputs into a single submission CSV.

Inputs (download both from SAS OnDemand → DS_Project folder):
  - churn_predictions.csv      : all scored test customers
  - retention_action_list.csv  : top-100 highest-risk customers (sorted desc by P_1)

Output:
  - Prediction_Results.csv     : single merged file, sorted by churn probability,
                                 with In_Action_List flag and Action_Rank column.
"""
import pandas as pd
from pathlib import Path

ROOT = Path("/Users/zeyadzaher/DS_Tools_Final_Project")
preds_path = ROOT / "churn_predictions.csv"
action_path = ROOT / "retention_action_list.csv"
out_path = ROOT / "Prediction_Results.csv"

if not preds_path.exists():
    raise SystemExit(
        f"Missing {preds_path.name}. Download it from SAS Studio first "
        f"(/home/u64514667/DS_Project/churn_predictions.csv)."
    )
if not action_path.exists():
    raise SystemExit(
        f"Missing {action_path.name}. Download it from SAS Studio first "
        f"(/home/u64514667/DS_Project/retention_action_list.csv)."
    )

preds = pd.read_csv(preds_path)
action = pd.read_csv(action_path)

print(f"churn_predictions.csv      : {len(preds):>5,} rows × {len(preds.columns)} cols")
print(f"retention_action_list.csv  : {len(action):>5,} rows × {len(action.columns)} cols")

# Find a stable join key. CustomerID is the natural identity column,
# but the prediction file from PROC LOGISTIC SCORE may not include it,
# so we fall back to row-order matching by P_1 + tier.
join_key = None
for candidate in ("CustomerID", "Customer_ID", "_NAME_"):
    if candidate in preds.columns and candidate in action.columns:
        join_key = candidate
        break

# Sort the full predictions by churn probability, descending
prob_col = next((c for c in preds.columns if c.upper() in ("P_1", "PROB", "CHURN_PROB")), "P_1")
preds = preds.sort_values(prob_col, ascending=False).reset_index(drop=True)

# Mark the action-list rows
preds["In_Action_List"] = "No"
preds["Action_Rank"] = ""

if join_key:
    action_keys = set(action[join_key].astype(str))
    preds["In_Action_List"] = preds[join_key].astype(str).isin(action_keys).map(
        {True: "Yes", False: "No"}
    )
    # Rank within action list by P_1 descending
    if "Action_Rank" in action.columns:
        rank_map = dict(zip(action[join_key].astype(str), action["Action_Rank"]))
    else:
        action_sorted = action.sort_values(prob_col, ascending=False).reset_index(drop=True)
        rank_map = {
            str(k): i + 1 for i, k in enumerate(action_sorted[join_key].astype(str))
        }
    preds["Action_Rank"] = preds[join_key].astype(str).map(rank_map).fillna("")
else:
    # Fallback: top N rows of the sorted predictions match the action list size
    top_n = len(action)
    preds.loc[: top_n - 1, "In_Action_List"] = "Yes"
    preds.loc[: top_n - 1, "Action_Rank"] = range(1, top_n + 1)

# Reorder columns: identity first, probability and tier next, rest after
priority_cols = [c for c in (
    "CustomerID", "Customer_ID",
    prob_col, "Predicted_Churn", "Predicted_Churn_Opt",
    "Risk_Tier", "In_Action_List", "Action_Rank", "Recommended_Action",
) if c in preds.columns]
remaining = [c for c in preds.columns if c not in priority_cols]
preds = preds[priority_cols + remaining]

preds.to_csv(out_path, index=False)

print(f"\nMerged → {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")
print(f"Total rows         : {len(preds):,}")
print(f"In action list     : {(preds['In_Action_List'] == 'Yes').sum()}")
print(f"Critical tier      : {(preds.get('Risk_Tier') == '1-Critical').sum() if 'Risk_Tier' in preds else 'n/a'}")
print(f"Columns            : {list(preds.columns)}")
