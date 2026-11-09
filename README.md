
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

## Project Features

- Synthetic payment transaction generation
- Data cleaning and preprocessing
- Payment reconciliation and retry tracking
- Refund classification and investigation
- Explainable rule-based anomaly detection
- SQLite database integration
- Interactive Streamlit analytics dashboard
- Transaction search and risk filtering
- PDF audit report generation
- CSV investigation queue export
- Automated data validation using unittest

## Technology Stack

Python 3.12, Pandas, SQLite, Streamlit,
Plotly, ReportLab, Git and GitHub.

## Run the Project

1. Create and activate a Python virtual environment.
2. Install dependencies:

   pip install -r requirements.txt

3. Generate the synthetic datasets:

   python generate_data.py

4. Execute the data pipeline:

   python run_pipeline.py
   python run_reconciliation.py
   python run_anomaly.py
   python run_database.py

5. Launch the dashboard:

   streamlit run app.py

6. Run automated tests:

   python -m unittest discover -s tests -v

## Testing

10 automated validation tests passed.

## Disclaimer

PayGuard uses synthetic financial data.
Anomaly flags are indicators for manual
investigation, not confirmed fraud.

This project is intended for educational
and demonstration purposes.
