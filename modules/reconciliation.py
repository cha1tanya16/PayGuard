
import pandas as pd
from pathlib import Path

DATA = Path("data/processed")
DATA.mkdir(parents=True, exist_ok=True)


def reconcile_payments():

    # Load cleaned datasets
    transactions = pd.read_csv(DATA / "transactions_clean.csv")
    payments = pd.read_csv(DATA / "payment_status_clean.csv")
    refunds = pd.read_csv(DATA / "refunds_clean.csv")

    # Convert timestamps
    payments["event_timestamp"] = pd.to_datetime(
        payments["event_timestamp"]
    )

    # 1. Sort payment events chronologically
    payments = payments.sort_values(
        ["event_timestamp", "attempt_no"]
    )

    # 2. Get the latest payment status for each transaction
    latest = payments.drop_duplicates(
        "transaction_id", keep="last"
    )[
        ["transaction_id", "payment_status", "attempt_no"]
    ]

    latest = latest.rename(columns={
        "payment_status": "final_payment_status",
        "attempt_no": "final_attempt"
    })

    # 3. Count all payment attempts
    attempts = payments.groupby(
        "transaction_id"
    ).size().reset_index(name="total_attempts")

    # 4. Calculate successfully processed refunds
    processed_refunds = refunds[
        refunds["refund_status"] == "PROCESSED"
    ]

    refund_summary = processed_refunds.groupby(
        "transaction_id"
    )["refund_amount"].sum().reset_index()

    refund_summary = refund_summary.rename(columns={
        "refund_amount": "total_refund"
    })

    # Count all refund records
    refund_counts = refunds.groupby(
        "transaction_id"
    ).size().reset_index(name="refund_count")

    # 5. Combine all information
    ledger = transactions.merge(
        latest, on="transaction_id", how="left"
    )

    ledger = ledger.merge(
        attempts, on="transaction_id", how="left"
    )

    ledger = ledger.merge(
        refund_summary, on="transaction_id", how="left"
    )

    ledger = ledger.merge(
        refund_counts, on="transaction_id", how="left"
    )

    ledger["final_payment_status"] = (
        ledger["final_payment_status"].fillna("UNKNOWN")
    )

    ledger["total_attempts"] = (
        ledger["total_attempts"].fillna(0).astype(int)
    )

    ledger["total_refund"] = ledger["total_refund"].fillna(0)
    ledger["refund_count"] = (
        ledger["refund_count"].fillna(0).astype(int)
    )

    # 6. Calculate successful payment amount
    ledger["successful_amount"] = ledger.apply(
        lambda row: row["amount"]
        if row["final_payment_status"] == "SUCCESS"
        else 0,
        axis=1
    )

    # 7. Calculate net amount
    ledger["net_amount"] = (
        ledger["successful_amount"] - ledger["total_refund"]
    )

    # 8. Classify refunds
    def classify_refund(row):
        if row["total_refund"] == 0:
            return "NO REFUND"
        if row["successful_amount"] == 0:
            return "REFUND WITHOUT SUCCESS"
        if row["total_refund"] > row["amount"]:
            return "EXCESSIVE REFUND"
        if row["total_refund"] == row["amount"]:
            return "FULL REFUND"
        return "PARTIAL REFUND"

    ledger["refund_classification"] = ledger.apply(
        classify_refund, axis=1
    )

    # 9. Generate reconciliation flags
    ledger["review_reason"] = ""

    ledger.loc[
        ledger["total_attempts"] >= 3,
        "review_reason"
    ] += "Multiple retries; "

    ledger.loc[
        ledger["refund_classification"] == "EXCESSIVE REFUND",
        "review_reason"
    ] += "Excessive refund; "

    ledger.loc[
        ledger["refund_classification"] == "REFUND WITHOUT SUCCESS",
        "review_reason"
    ] += "Refund without successful payment; "

    ledger["review_required"] = (
        ledger["review_reason"] != ""
    )

    # 10. Save reconciled ledger
    ledger.to_csv(DATA / "reconciled_ledger.csv", index=False)

    print("\nPAYMENT RECONCILIATION COMPLETED")
    print("Unique transactions:", len(ledger))
    print("Successful payments:",
          (ledger["final_payment_status"] == "SUCCESS").sum())
    print("Total processed refunds:",
          round(ledger["total_refund"].sum(), 2))
    print("Transactions requiring review:",
          ledger["review_required"].sum())

    print("\nRefund classification:")
    print(ledger["refund_classification"].value_counts())

    print("\nLedger saved to data/processed/reconciled_ledger.csv")

    return ledger


if __name__ == "__main__":
    reconcile_payments()
