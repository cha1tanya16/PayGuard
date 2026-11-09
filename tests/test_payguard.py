
import sqlite3
import unittest
from pathlib import Path

import pandas as pd

DB = Path("database/payguard.db")


class TestPayGuard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not DB.exists():
            raise FileNotFoundError(
                "Run python run_database.py first"
            )

        cls.conn = sqlite3.connect(DB)
        cls.transactions = pd.read_sql(
            "SELECT * FROM transactions", cls.conn
        )
        cls.ledger = pd.read_sql(
            "SELECT * FROM reconciled_ledger", cls.conn
        )
        cls.anomalies = pd.read_sql(
            "SELECT * FROM anomaly_results", cls.conn
        )
        cls.events = pd.read_sql(
            "SELECT * FROM payment_events", cls.conn
        )

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_transaction_ids_unique(self):
        self.assertTrue(
            self.transactions["transaction_id"].is_unique
        )

    def test_ledger_count(self):
        self.assertEqual(
            len(self.transactions), len(self.ledger)
        )

    def test_ledger_ids_match(self):
        self.assertEqual(
            set(self.transactions["transaction_id"]),
            set(self.ledger["transaction_id"])
        )

    def test_anomaly_count(self):
        self.assertEqual(
            len(self.transactions), len(self.anomalies)
        )

    def test_no_negative_transaction_amounts(self):
        self.assertTrue(
            (self.transactions["amount"] >= 0).all()
        )

    def test_valid_payment_status(self):
        valid = {"SUCCESS", "FAILED", "PENDING"}
        self.assertTrue(
            set(self.ledger["final_payment_status"])
            .issubset(valid)
        )

    def test_valid_risk_levels(self):
        valid = {"LOW", "MEDIUM", "HIGH"}
        self.assertTrue(
            set(self.anomalies["risk_level"])
            .issubset(valid)
        )

    def test_no_duplicate_payment_events(self):
        self.assertFalse(
            self.events.duplicated().any()
        )

    def test_refund_amounts_nonnegative(self):
        self.assertTrue(
            (self.ledger["total_refund"] >= 0).all()
        )

    def test_risk_scores_nonnegative(self):
        self.assertTrue(
            (self.anomalies["risk_score"] >= 0).all()
        )


if __name__ == "__main__":
    unittest.main()
