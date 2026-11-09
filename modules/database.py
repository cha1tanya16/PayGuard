
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/payguard.db")
DATA_PATH = Path("data/processed")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_database():

    connection = sqlite3.connect(DB_PATH)

    datasets = {
        "customers": "customers_clean.csv",
        "merchants": "merchants_clean.csv",
        "transactions": "transactions_clean.csv",
        "payment_events": "payment_status_clean.csv",
        "refunds": "refunds_clean.csv",
        "devices": "device_summary_clean.csv",
        "reconciled_ledger": "reconciled_ledger.csv",
        "anomaly_results": "anomaly_results.csv"
    }

    for table, filename in datasets.items():

        file_path = DATA_PATH / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"{filename} not found. Run earlier phases first."
            )

        df = pd.read_csv(file_path)

        df.to_sql(
            table,
            connection,
            if_exists="replace",
            index=False
        )

        print(f"Loaded {table}: {len(df)} records")

    # Create indexes for frequently queried columns
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_transaction_id "
        "ON transactions(transaction_id)"
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_customer_id "
        "ON transactions(customer_id)"
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_risk_score "
        "ON anomaly_results(risk_score)"
    )

    connection.commit()
    connection.close()

    print("\nPayGuard SQLite database created successfully!")


def query_database(sql):

    connection = sqlite3.connect(DB_PATH)
    result = pd.read_sql_query(sql, connection)
    connection.close()

    return result


if __name__ == "__main__":
    load_database()
