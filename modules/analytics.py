
from modules.database import query_database


def get_dashboard_metrics():

    queries = {
        "total_transactions": """
            SELECT COUNT(*) AS value FROM transactions
        """,

        "total_volume": """
            SELECT ROUND(SUM(amount), 2) AS value
            FROM transactions
        """,

        "successful_payments": """
            SELECT COUNT(*) AS value
            FROM anomaly_results
            WHERE final_payment_status = 'SUCCESS'
        """,

        "flagged_transactions": """
            SELECT COUNT(*) AS value
            FROM anomaly_results
            WHERE anomaly_detected = 1
        """,

        "high_risk_transactions": """
            SELECT COUNT(*) AS value
            FROM anomaly_results
            WHERE risk_level = 'HIGH'
        """,

        "processed_refunds": """
            SELECT ROUND(SUM(total_refund), 2) AS value
            FROM reconciled_ledger
        """
    }

    return {
        name: query_database(sql).iloc[0]["value"]
        for name, sql in queries.items()
    }


def get_risk_distribution():

    return query_database("""
        SELECT risk_level, COUNT(*) AS total
        FROM anomaly_results
        GROUP BY risk_level
    """)


def get_merchant_analysis():

    return query_database("""
        SELECT
            merchant_id,
            COUNT(*) AS transaction_count,
            ROUND(SUM(amount), 2) AS total_volume,
            ROUND(AVG(amount), 2) AS average_amount
        FROM transactions
        GROUP BY merchant_id
        ORDER BY total_volume DESC
    """)


def get_review_queue():

    return query_database("""
        SELECT
            transaction_id,
            amount,
            final_payment_status,
            total_refund,
            risk_score,
            risk_level,
            anomaly_reasons
        FROM anomaly_results
        WHERE anomaly_detected = 1
        ORDER BY risk_score DESC
    """)
