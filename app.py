
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from pathlib import Path
from modules.audit_reports import create_review_csv, create_audit_pdf

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------
st.set_page_config(
    page_title="PayGuard | Transaction Monitoring",
    page_icon="🛡️",
    layout="wide"
)

DB_PATH = Path("database/payguard.db")


# -------------------------------------------------
# DATABASE FUNCTIONS
# -------------------------------------------------
@st.cache_data
def load_table(table):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table}", conn)


if not DB_PATH.exists():
    st.error("Database not found. Run: python run_database.py")
    st.stop()

transactions = load_table("transactions")
ledger = load_table("reconciled_ledger")
anomalies = load_table("anomaly_results")
refunds = load_table("refunds")
merchants = load_table("merchants")
customers = load_table("customers")
payments = load_table("payment_events")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("🛡️ PayGuard")
st.sidebar.caption("Transaction Intelligence Platform")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Payment Analytics",
        "Refund Analysis",
        "Risk Analytics",
        "Merchant Analysis",
        "Transaction Explorer",
        "Investigation Queue",
        "Audit Reports"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Data source: PayGuard SQLite Database")
st.sidebar.caption("Dataset: Synthetic transaction records")


# -------------------------------------------------
# COMMON METRICS
# -------------------------------------------------
total_transactions = len(ledger)

successful = (
    ledger["final_payment_status"] == "SUCCESS"
).sum()

failed = (
    ledger["final_payment_status"] == "FAILED"
).sum()

total_volume = ledger["amount"].sum()

total_refunds = ledger["total_refund"].sum()

flagged = anomalies["anomaly_detected"].sum()

high_risk = (
    anomalies["risk_level"] == "HIGH"
).sum()

success_rate = (
    successful / total_transactions * 100
    if total_transactions else 0
)


def show_metrics():
    cols = st.columns(4)

    metrics = [
        ("Total Transactions", f"{total_transactions:,}"),
        ("Transaction Volume", f"₹{total_volume:,.0f}"),
        ("Successful Payments", f"{successful:,}"),
        ("Flagged Transactions", f"{flagged:,}")
    ]

    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


def transaction_details(transaction_id):

    txn = ledger[
        ledger["transaction_id"] == transaction_id
    ]

    payment_records = payments[
        payments["transaction_id"] == transaction_id
    ].sort_values("attempt_no")

    refund_records = refunds[
        refunds["transaction_id"] == transaction_id
    ]

    risk_record = anomalies[
        anomalies["transaction_id"] == transaction_id
    ]

    st.subheader(f"Transaction: {transaction_id}")

    if not txn.empty:
        st.write("Reconciled payment details")
        st.dataframe(txn, use_container_width=True)

    st.write("Payment event history")
    st.dataframe(payment_records, use_container_width=True)

    st.write("Refund records")
    if refund_records.empty:
        st.info("No refund records found.")
    else:
        st.dataframe(refund_records, use_container_width=True)

    st.write("Risk assessment")
    if not risk_record.empty:
        st.dataframe(
            risk_record[
                [
                    "risk_score",
                    "risk_level",
                    "anomaly_reasons"
                ]
            ],
            use_container_width=True
        )


# -------------------------------------------------
# PAGE 1: OVERVIEW
# -------------------------------------------------
if page == "Overview":

    st.title("PayGuard Dashboard")
    st.write(
        "Monitor payment activity, refund patterns "
        "and suspicious transactions."
    )

    show_metrics()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payment Status Distribution")

        status_data = ledger[
            "final_payment_status"
        ].value_counts().reset_index()

        status_data.columns = ["Status", "Count"]

        fig = px.pie(
            status_data,
            names="Status",
            values="Count",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk Level Distribution")

        risk_data = anomalies[
            "risk_level"
        ].value_counts().reset_index()

        risk_data.columns = ["Risk Level", "Count"]

        fig = px.bar(
            risk_data,
            x="Risk Level",
            y="Count",
            color="Risk Level",
            text="Count"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Key Performance Indicators")

    c1, c2, c3 = st.columns(3)

    c1.metric("Payment Success Rate", f"{success_rate:.1f}%")
    c2.metric("Processed Refund Amount", f"₹{total_refunds:,.2f}")
    c3.metric("High-Risk Transactions", f"{high_risk:,}")

    st.subheader("Latest Transactions")

    st.dataframe(
        ledger.sort_values(
            "timestamp", ascending=False
        ).head(10),
        use_container_width=True
    )


# -------------------------------------------------
# PAGE 2: PAYMENT ANALYTICS
# -------------------------------------------------
elif page == "Payment Analytics":

    st.title("Payment Analytics")
    st.write("Analyse payment outcomes and retry behaviour.")

    show_metrics()

    status_data = ledger[
        "final_payment_status"
    ].value_counts().reset_index()

    status_data.columns = ["Payment Status", "Transactions"]

    fig = px.bar(
        status_data,
        x="Payment Status",
        y="Transactions",
        color="Payment Status",
        text="Transactions",
        title="Final Payment Status"
    )

    st.plotly_chart(fig, use_container_width=True)

    retry_data = ledger["total_attempts"].value_counts().reset_index()
    retry_data.columns = ["Attempts", "Transactions"]

    fig = px.bar(
        retry_data,
        x="Attempts",
        y="Transactions",
        text="Transactions",
        title="Payment Attempts Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payment Records")

    st.dataframe(
        ledger[
            [
                "transaction_id",
                "amount",
                "final_payment_status",
                "total_attempts",
                "successful_amount"
            ]
        ],
        use_container_width=True
    )


# -------------------------------------------------
# PAGE 3: REFUND ANALYSIS
# -------------------------------------------------
elif page == "Refund Analysis":

    st.title("Refund Analysis")

    refund_data = ledger[
        "refund_classification"
    ].value_counts().reset_index()

    refund_data.columns = ["Refund Type", "Count"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            refund_data,
            names="Refund Type",
            values="Count",
            hole=0.45,
            title="Refund Classification"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            refund_data,
            x="Refund Type",
            y="Count",
            color="Refund Type",
            title="Refund Categories"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.metric("Total Processed Refunds", f"₹{total_refunds:,.2f}")

    st.subheader("Refund Records")

    st.dataframe(
        refunds,
        use_container_width=True
    )

    st.subheader("Transactions Requiring Refund Investigation")

    refund_issues = ledger[
        ledger["refund_classification"].isin(
            [
                "EXCESSIVE REFUND",
                "REFUND WITHOUT SUCCESS"
            ]
        )
    ]

    st.dataframe(refund_issues, use_container_width=True)


# -------------------------------------------------
# PAGE 4: RISK ANALYTICS
# -------------------------------------------------
elif page == "Risk Analytics":

    st.title("Risk Analytics")
    st.write("Review explainable transaction risk scores.")

    c1, c2, c3 = st.columns(3)

    c1.metric("Flagged Transactions", f"{flagged:,}")
    c2.metric("High Risk", f"{high_risk:,}")
    c3.metric(
        "Average Risk Score",
        f"{anomalies['risk_score'].mean():.1f}"
    )

    risk_data = anomalies[
        "risk_level"
    ].value_counts().reset_index()

    risk_data.columns = ["Risk Level", "Count"]

    fig = px.pie(
        risk_data,
        names="Risk Level",
        values="Count",
        hole=0.4,
        title="Risk Classification"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(
        anomalies,
        x="risk_score",
        nbins=20,
        title="Risk Score Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk Score Records")

    st.dataframe(
        anomalies[
            [
                "transaction_id",
                "amount",
                "risk_score",
                "risk_level",
                "anomaly_reasons"
            ]
        ].sort_values("risk_score", ascending=False),
        use_container_width=True
    )


# -------------------------------------------------
# PAGE 5: MERCHANT ANALYSIS
# -------------------------------------------------
elif page == "Merchant Analysis":

    st.title("Merchant Analytics")

    merchant_data = transactions.merge(
        merchants,
        on="merchant_id",
        how="left"
    )

    summary = merchant_data.groupby(
        ["merchant_id", "merchant_name", "category"]
    ).agg(
        transaction_count=("transaction_id", "count"),
        total_volume=("amount", "sum"),
        average_amount=("amount", "mean")
    ).reset_index()

    summary = summary.sort_values(
        "total_volume", ascending=False
    )

    fig = px.bar(
        summary.head(10),
        x="merchant_name",
        y="total_volume",
        color="category",
        title="Top 10 Merchants by Transaction Volume"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Merchant Performance")

    st.dataframe(summary, use_container_width=True)


# -------------------------------------------------
# PAGE 6: TRANSACTION EXPLORER
# -------------------------------------------------
elif page == "Transaction Explorer":

    st.title("Transaction Explorer")

    search_id = st.text_input(
        "Search by Transaction ID",
        placeholder="Example: TXN0001"
    )

    filtered = ledger.copy()

    statuses = sorted(
        filtered["final_payment_status"].dropna().unique()
    )

    selected_status = st.multiselect(
        "Filter Payment Status",
        statuses,
        default=statuses
    )

    filtered = filtered[
        filtered["final_payment_status"].isin(selected_status)
    ]

    if search_id.strip():
        filtered = filtered[
            filtered["transaction_id"].str.contains(
                search_id.strip(),
                case=False,
                na=False
            )
        ]

    st.write(f"Records found: {len(filtered)}")

    st.dataframe(filtered, use_container_width=True)

    if not filtered.empty:
        selected_id = st.selectbox(
            "Inspect Transaction",
            filtered["transaction_id"].tolist()
        )

        transaction_details(selected_id)


# -------------------------------------------------
# PAGE 7: INVESTIGATION QUEUE
# -------------------------------------------------
elif page == "Investigation Queue":

    st.title("Investigation Queue")

    st.warning(
        "Flagged records are candidates for manual review, "
        "not confirmed fraud."
    )

    review = anomalies[
        anomalies["anomaly_detected"] == 1
    ].copy()

    levels = ["HIGH", "MEDIUM", "LOW"]

    selected_levels = st.multiselect(
        "Filter Risk Level",
        levels,
        default=levels
    )

    review = review[
        review["risk_level"].isin(selected_levels)
    ].sort_values("risk_score", ascending=False)

    st.metric("Transactions in Current Queue", len(review))

    st.dataframe(
        review[
            [
                "transaction_id",
                "amount",
                "final_payment_status",
                "total_refund",
                "risk_score",
                "risk_level",
                "anomaly_reasons"
            ]
        ],
        use_container_width=True
    )

    if not review.empty:

        selected_id = st.selectbox(
            "Select Transaction for Investigation",
            review["transaction_id"].tolist()
        )

        transaction_details(selected_id)

# -------------------------------------------------
# PAGE 8: AUDIT REPORTS
# -------------------------------------------------
elif page == "Audit Reports":

    st.title("Audit Reports")
    st.write(
        "Generate downloadable reports for transaction "
        "monitoring and manual investigation."
    )

    flagged_records = anomalies[
        anomalies["anomaly_detected"] == 1
    ]

    high_risk_records = anomalies[
        anomalies["risk_level"] == "HIGH"
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Transactions", len(ledger))
    c2.metric("Flagged Records", len(flagged_records))
    c3.metric("High-Risk Records", len(high_risk_records))

    st.divider()

    st.subheader("Download Reports")

    st.download_button(
        label="Download Investigation Queue (CSV)",
        data=create_review_csv(anomalies),
        file_name="payguard_investigation_queue.csv",
        mime="text/csv"
    )

    pdf_data = create_audit_pdf(ledger, anomalies)

    st.download_button(
        label="Download Audit Report (PDF)",
        data=pdf_data,
        file_name="payguard_audit_report.pdf",
        mime="application/pdf"
    )

    st.divider()

    st.subheader("Audit Summary")

    st.write(
        f"Total transaction volume: ₹{ledger['amount'].sum():,.2f}"
    )

    st.write(
        f"Total refund amount: ₹{ledger['total_refund'].sum():,.2f}"
    )

    st.write(
        f"Payment success rate: "
        f"{(ledger['final_payment_status'] == 'SUCCESS').mean() * 100:.2f}%"
    )

    st.write(
        f"High-risk records: {len(high_risk_records)}"
    )

    st.info(
        "All flagged records require manual review. "
        "Anomaly detection does not confirm fraudulent activity."
    )
        


# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.sidebar.divider()
st.sidebar.caption("PayGuard | Academic Data Engineering Project")
st.sidebar.caption("Synthetic data – not a live payment system")
