
# PayGuard - Transaction Anomaly & Refund Investigation System

PayGuard is an end-to-end data engineering project designed to monitor online payment transactions, reconcile payment lifecycles, and identify unusual transaction and refund patterns.

## Problem Statement

Duplicate payment events, repeated payment attempts, partial refunds, and inconsistent payment statuses make financial transaction monitoring difficult.

PayGuard processes transaction-related datasets to identify data inconsistencies and generate an explainable investigation queue.

## Key Features

- Synthetic payment dataset generation
- Data cleaning and preprocessing
- Duplicate event detection
- Payment lifecycle reconciliation
- Partial and full refund analysis
- Explainable anomaly detection
- Transaction analytics dashboard
- Audit report generation

## Technology Stack

- Python
- Pandas and NumPy
- SQLite
- SQL
- Streamlit
- Plotly

## Project Structure

PayGuard/
- data/
- database/
- modules/
- reports/
- generate_data.py
- app.py
- requirements.txt

## Installation

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies.

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install libraries:

```bash
pip install -r requirements.txt
```

## Run the Application

Generate datasets:

```bash
python generate_data.py
```

Launch PayGuard:

```bash
streamlit run app.py
```

## Dataset

The project uses synthetic transaction, customer, merchant, refund, payment status, and device summary data.

No real customer or payment information is used.

## Project Status

Currently under development.

## Author

Chaitanya Mevekari

B.Tech - Computer Science and Engineering
