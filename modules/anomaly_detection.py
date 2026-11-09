
import pandas as pd
from pathlib import Path

DATA = Path("data/processed")


def detect_anomalies():

    # Load reconciled ledger and device information
    ledger = pd.read_csv(DATA / "reconciled_ledger.csv")
    devices = pd.read_csv(DATA / "device_summary_clean.csv")

    # Add device information
    ledger = ledger.merge(
        devices[["customer_id", "device_count", "risk_indicator"]],
        on="customer_id",
        how="left"
    )

    ledger["device_count"] = ledger["device_count"].fillna(0)
    ledger["risk_indicator"] = (
        ledger["risk_indicator"].fillna("UNKNOWN")
    )

    # Set high transaction amount threshold (95th percentile)
    amount_limit = ledger["amount"].quantile(0.95)

    # Initialise risk scores and explanations
    ledger["risk_score"] = 0
    ledger["anomaly_reasons"] = ""

    def flag(condition, points, reason):
        ledger.loc[condition, "risk_score"] += points
        ledger.loc[condition, "anomaly_reasons"] += reason + "; "

    # Rule 1: Multiple payment retries
    flag(
        ledger["total_attempts"] >= 3,
        20,
        "Multiple payment retries"
    )

    # Rule 2: Excessive refund
    flag(
        ledger["refund_classification"] == "EXCESSIVE REFUND",
        35,
        "Refund exceeds transaction amount"
    )

    # Rule 3: Refund without successful payment
    flag(
        ledger["refund_classification"] == "REFUND WITHOUT SUCCESS",
        35,
        "Refund without successful payment"
    )

    # Rule 4: High-risk device
    flag(
        ledger["risk_indicator"] == "HIGH",
        30,
        "High-risk device"
    )

    # Rule 5: Unusually high device count
    flag(
        ledger["device_count"] >= 3,
        10,
        "Multiple devices used"
    )

    # Rule 6: Multiple refund records
    flag(
        ledger["refund_count"] >= 2,
        10,
        "Multiple refund requests"
    )

    # Rule 7: Unusually large transaction
    flag(
        ledger["amount"] >= amount_limit,
        10,
        "Unusually high transaction amount"
    )

    # Limit score to 100
    ledger["risk_score"] = ledger["risk_score"].clip(upper=100)

    # Assign risk levels
    ledger["risk_level"] = pd.cut(
        ledger["risk_score"],
        bins=[-1, 19, 49, 100],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    ledger["anomaly_detected"] = ledger["risk_score"] > 0

    # Create prioritised review queue
    review_queue = ledger[
        ledger["anomaly_detected"]
    ].sort_values(
        "risk_score",
        ascending=False
    )

    # Save results
    ledger.to_csv(DATA / "anomaly_results.csv", index=False)
    review_queue.to_csv(DATA / "review_queue.csv", index=False)

    # Summary measures
    print("\nPAYGUARD ANOMALY DETECTION RESULTS")
    print("----------------------------------")
    print("Total transactions:", len(ledger))
    print("Flagged transactions:", len(review_queue))
    print("High-risk transactions:",
          (ledger["risk_level"] == "HIGH").sum())
    print("Medium-risk transactions:",
          (ledger["risk_level"] == "MEDIUM").sum())
    print("Low-risk transactions:",
          (ledger["risk_level"] == "LOW").sum())
    print("High amount threshold:", round(amount_limit, 2))

    print("\nRisk level distribution:")
    print(ledger["risk_level"].value_counts())

    print("\nTop 10 transactions for investigation:")
    print(
        review_queue[
            [
                "transaction_id",
                "amount",
                "risk_score",
                "risk_level",
                "anomaly_reasons"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nFiles saved:")
    print("anomaly_results.csv")
    print("review_queue.csv")

    return ledger, review_queue


if __name__ == "__main__":
    detect_anomalies()
