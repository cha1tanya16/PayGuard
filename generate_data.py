
import pandas as pd
import random
import os

random.seed(42)
os.makedirs("data", exist_ok=True)

# 1. Customers
customers = pd.DataFrame([
    {
        "customer_id": f"C{i:04}",
        "customer_name": f"Customer {i}",
        "location": random.choice(
            ["Pune", "Mumbai", "Delhi", "Bangalore", "Chennai"]
        )
    }
    for i in range(1, 201)
])

# 2. Merchants
merchants = pd.DataFrame([
    {
        "merchant_id": f"M{i:03}",
        "merchant_name": f"Merchant {i}",
        "category": random.choice(
            ["Shopping", "Food", "Travel", "Electronics", "Services"]
        )
    }
    for i in range(1, 31)
])

# 3. Transactions
transactions = pd.DataFrame([
    {
        "transaction_id": f"TXN{i:04}",
        "customer_id": f"C{random.randint(1, 200):04}",
        "merchant_id": f"M{random.randint(1, 30):03}",
        "amount": random.choice(
            [250, 500, 750, 1000, 1500, 2500, 5000, 10000, 25000]
        ),
        "timestamp": pd.Timestamp("2026-01-01")
        + pd.Timedelta(
            days=random.randint(0, 300),
            minutes=random.randint(0, 1440)
        )
    }
    for i in range(1, 501)
])

# 4. Payment status events
payment_events = []
event_number = 1

for _, txn in transactions.iterrows():
    attempts = random.choices(
        [1, 2, 3], weights=[70, 23, 7]
    )[0]

    for attempt in range(attempts):
        if attempt == attempts - 1:
            status = random.choices(
                ["SUCCESS", "FAILED", "PENDING"],
                weights=[75, 20, 5]
            )[0]
        else:
            status = "FAILED"

        payment_events.append({
            "event_id": f"EVT{event_number:05}",
            "transaction_id": txn["transaction_id"],
            "attempt_no": attempt + 1,
            "payment_status": status,
            "event_timestamp": txn["timestamp"]
            + pd.Timedelta(minutes=attempt * 2)
        })
        event_number += 1

payment_status = pd.DataFrame(payment_events)

# Add 15 duplicate events
duplicates = payment_status.sample(15, random_state=42)
payment_status = pd.concat(
    [payment_status, duplicates],
    ignore_index=True
)

# 5. Refunds
successful_ids = set(
    payment_status.loc[
        payment_status["payment_status"] == "SUCCESS",
        "transaction_id"
    ]
)

refunds = []
refund_number = 1

for _, txn in transactions.iterrows():
    if (
        txn["transaction_id"] in successful_ids
        and random.random() < 0.20
    ):
        amount = txn["amount"]

        refund_amount = amount * random.choice(
            [0.25, 0.50, 1.00, 1.20]
        )

        refunds.append({
            "refund_id": f"REF{refund_number:04}",
            "transaction_id": txn["transaction_id"],
            "refund_amount": refund_amount,
            "refund_status": random.choice(
                ["PROCESSED", "PENDING", "FAILED"]
            )
        })
        refund_number += 1

refunds = pd.DataFrame(refunds)

# 6. Device summary
devices = pd.DataFrame([
    {
        "customer_id": customer_id,
        "device_id": f"DEV{random.randint(1, 350):04}",
        "device_count": random.choice([1, 1, 2, 2, 3, 5]),
        "risk_indicator": random.choice(
            ["LOW", "LOW", "MEDIUM", "HIGH"]
        )
    }
    for customer_id in customers["customer_id"]
])

# Save all datasets
datasets = {
    "transactions.csv": transactions,
    "customers.csv": customers,
    "merchants.csv": merchants,
    "refunds.csv": refunds,
    "payment_status.csv": payment_status,
    "device_summary.csv": devices
}

for filename, df in datasets.items():
    df.to_csv(f"data/{filename}", index=False)
    print(f"{filename}: {len(df)} records")

print("\nAll six datasets generated successfully!")
