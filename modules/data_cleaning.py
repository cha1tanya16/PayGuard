
import pandas as pd
from pathlib import Path

DATA = Path("data")
PROCESSED = DATA / "processed"
REJECTED = DATA / "rejected"

PROCESSED.mkdir(parents=True, exist_ok=True)
REJECTED.mkdir(parents=True, exist_ok=True)

quality_report = []


def record_quality(name, original, cleaned, rejected=0, duplicates=0):
    quality_report.append({
        "dataset": name,
        "original_records": original,
        "clean_records": cleaned,
        "rejected_records": rejected,
        "duplicate_records": duplicates
    })


def save_rejected(df, filename):
    df.to_csv(REJECTED / filename, index=False)


def save_clean(df, filename):
    df.to_csv(PROCESSED / filename, index=False)


# 1. Load all raw datasets
transactions = pd.read_csv(DATA / "transactions.csv")
customers = pd.read_csv(DATA / "customers.csv")
merchants = pd.read_csv(DATA / "merchants.csv")
refunds = pd.read_csv(DATA / "refunds.csv")
payments = pd.read_csv(DATA / "payment_status.csv")
devices = pd.read_csv(DATA / "device_summary.csv")

print("All six datasets loaded successfully.")


# 2. Clean transactions
original = len(transactions)

transactions["amount"] = pd.to_numeric(
    transactions["amount"], errors="coerce"
)
transactions["timestamp"] = pd.to_datetime(
    transactions["timestamp"], errors="coerce"
)

invalid = (
    transactions["transaction_id"].isna()
    | transactions["customer_id"].isna()
    | transactions["merchant_id"].isna()
    | transactions["amount"].isna()
    | (transactions["amount"] <= 0)
    | transactions["timestamp"].isna()
)

bad = transactions[invalid]
save_rejected(bad, "invalid_transactions.csv")

transactions = transactions[~invalid].copy()
transactions = transactions.drop_duplicates(
    subset="transaction_id", keep="first"
)

record_quality(
    "transactions", original, len(transactions), len(bad),
    original - len(bad) - len(transactions)
)


# 3. Clean customers
original = len(customers)

customers["location"] = customers["location"].fillna("Unknown")
bad = customers[customers["customer_id"].isna()]
save_rejected(bad, "invalid_customers.csv")

customers = customers.dropna(subset=["customer_id"])
customers = customers.drop_duplicates(subset="customer_id")

record_quality(
    "customers", original, len(customers), len(bad),
    original - len(bad) - len(customers)
)


# 4. Clean merchants
original = len(merchants)

merchants["category"] = merchants["category"].fillna("Unknown")
bad = merchants[merchants["merchant_id"].isna()]
save_rejected(bad, "invalid_merchants.csv")

merchants = merchants.dropna(subset=["merchant_id"])
merchants = merchants.drop_duplicates(subset="merchant_id")

record_quality(
    "merchants", original, len(merchants), len(bad),
    original - len(bad) - len(merchants)
)


# 5. Clean payment events
original = len(payments)

payments["payment_status"] = (
    payments["payment_status"].astype(str).str.strip().str.upper()
)
payments["event_timestamp"] = pd.to_datetime(
    payments["event_timestamp"], errors="coerce"
)
payments["attempt_no"] = pd.to_numeric(
    payments["attempt_no"], errors="coerce"
)

invalid = (
    payments["event_id"].isna()
    | payments["transaction_id"].isna()
    | payments["event_timestamp"].isna()
    | payments["attempt_no"].isna()
    | ~payments["payment_status"].isin(
        ["SUCCESS", "FAILED", "PENDING"]
    )
)

bad = payments[invalid]
save_rejected(bad, "invalid_payment_events.csv")
payments = payments[~invalid].copy()

before_dedup = len(payments)
payments = payments.drop_duplicates(
    subset="event_id", keep="first"
)
duplicates = before_dedup - len(payments)

record_quality(
    "payment_status", original, len(payments), len(bad), duplicates
)


# 6. Clean refunds
original = len(refunds)

refunds["refund_amount"] = pd.to_numeric(
    refunds["refund_amount"], errors="coerce"
)
refunds["refund_status"] = (
    refunds["refund_status"].astype(str).str.strip().str.upper()
)

invalid = (
    refunds["refund_id"].isna()
    | refunds["transaction_id"].isna()
    | refunds["refund_amount"].isna()
    | (refunds["refund_amount"] <= 0)
    | ~refunds["refund_status"].isin(
        ["PROCESSED", "PENDING", "FAILED"]
    )
)

bad = refunds[invalid]
save_rejected(bad, "invalid_refunds.csv")
refunds = refunds[~invalid].copy()
refunds = refunds.drop_duplicates(subset="refund_id")

record_quality(
    "refunds", original, len(refunds), len(bad),
    original - len(bad) - len(refunds)
)


# 7. Clean device summary
original = len(devices)

devices["device_count"] = pd.to_numeric(
    devices["device_count"], errors="coerce"
)
devices["risk_indicator"] = (
    devices["risk_indicator"].astype(str).str.strip().str.upper()
)

invalid = (
    devices["customer_id"].isna()
    | devices["device_id"].isna()
    | devices["device_count"].isna()
    | (devices["device_count"] < 1)
    | ~devices["risk_indicator"].isin(
        ["LOW", "MEDIUM", "HIGH"]
    )
)

bad = devices[invalid]
save_rejected(bad, "invalid_devices.csv")
devices = devices[~invalid].copy()
devices = devices.drop_duplicates(
    subset=["customer_id", "device_id"]
)

record_quality(
    "device_summary", original, len(devices), len(bad),
    original - len(bad) - len(devices)
)


# 8. Validate relationships between datasets
valid_customers = set(customers["customer_id"])
valid_merchants = set(merchants["merchant_id"])
valid_transactions = set(transactions["transaction_id"])

bad = transactions[
    ~transactions["customer_id"].isin(valid_customers)
    | ~transactions["merchant_id"].isin(valid_merchants)
]

# Save invalid relationships separately
save_rejected(bad, "invalid_transaction_references.csv")

transactions = transactions[
    transactions["customer_id"].isin(valid_customers)
    & transactions["merchant_id"].isin(valid_merchants)
].copy()

# Remove payment events and refunds with unknown transactions
payments = payments[
    payments["transaction_id"].isin(valid_transactions)
].copy()

refunds = refunds[
    refunds["transaction_id"].isin(valid_transactions)
].copy()

devices = devices[
    devices["customer_id"].isin(valid_customers)
].copy()


# 9. Combine transaction-related information
enriched = transactions.merge(
    customers, on="customer_id", how="left"
)

enriched = enriched.merge(
    merchants, on="merchant_id", how="left"
)

enriched = enriched.merge(
    devices[["customer_id", "device_count", "risk_indicator"]],
    on="customer_id", how="left"
)


# 10. Save cleaned datasets
save_clean(transactions, "transactions_clean.csv")
save_clean(customers, "customers_clean.csv")
save_clean(merchants, "merchants_clean.csv")
save_clean(payments, "payment_status_clean.csv")
save_clean(refunds, "refunds_clean.csv")
save_clean(devices, "device_summary_clean.csv")
save_clean(enriched, "transaction_enriched.csv")


# 11. Generate data quality report
report = pd.DataFrame(quality_report)
report.to_csv(PROCESSED / "data_quality_report.csv", index=False)

print("\nDATA CLEANING COMPLETED")
print(report.to_string(index=False))
print("\nProcessed files saved in data/processed/")
print("Rejected records saved in data/rejected/")
