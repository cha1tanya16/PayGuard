
from modules.database import load_database, query_database

# Load all processed data into SQLite
load_database()

# Test 1: Total transactions
print("\nTotal Transactions:")
print(query_database(
    "SELECT COUNT(*) AS total FROM transactions"
))

# Test 2: Average transaction amount
print("\nAverage Transaction Amount:")
print(query_database(
    "SELECT ROUND(AVG(amount), 2) AS average_amount "
    "FROM transactions"
))

# Test 3: Risk distribution
print("\nRisk Distribution:")
print(query_database(
    "SELECT risk_level, COUNT(*) AS total "
    "FROM anomaly_results GROUP BY risk_level"
))

# Test 4: High-risk transactions
print("\nHigh-Risk Transactions:")
print(query_database(
    "SELECT transaction_id, amount, risk_score, anomaly_reasons "
    "FROM anomaly_results "
    "WHERE risk_level = 'HIGH' "
    "ORDER BY risk_score DESC LIMIT 10"
))
