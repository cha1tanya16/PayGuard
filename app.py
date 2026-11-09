
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="PayGuard",
    page_icon="🛡️",
    layout="wide"
)

st.title("PayGuard")
st.subheader("Transaction Anomaly & Refund Investigation System")

st.markdown(
    "Monitor payments, reconcile transaction records "
    "and investigate unusual activity."
)

files = [
    "transactions.csv",
    "customers.csv",
    "merchants.csv",
    "refunds.csv",
    "payment_status.csv",
    "device_summary.csv"
]

st.header("Dataset Overview")

columns = st.columns(3)

for i, filename in enumerate(files):
    path = os.path.join("data", filename)

    if os.path.exists(path):
        df = pd.read_csv(path)

        with columns[i % 3]:
            st.metric(
                filename.replace(".csv", "").replace("_", " ").title(),
                len(df)
            )
    else:
        st.warning(f"{filename} not found!")

st.success("PayGuard dataset check completed.")
