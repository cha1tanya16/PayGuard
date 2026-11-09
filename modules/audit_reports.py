
from io import BytesIO
from datetime import datetime

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet


def create_review_csv(anomalies):

    review = anomalies[
        anomalies["anomaly_detected"] == 1
    ].copy()

    review = review.sort_values(
        "risk_score",
        ascending=False
    )

    return review.to_csv(index=False).encode("utf-8")


def create_audit_pdf(ledger, anomalies):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    content = []

    total = len(ledger)

    successful = (
        ledger["final_payment_status"] == "SUCCESS"
    ).sum()

    failed = (
        ledger["final_payment_status"] == "FAILED"
    ).sum()

    pending = (
        ledger["final_payment_status"] == "PENDING"
    ).sum()

    flagged = (
        anomalies["anomaly_detected"] == 1
    ).sum()

    high_risk = (
        anomalies["risk_level"] == "HIGH"
    ).sum()

    refund_total = ledger["total_refund"].sum()

    content.append(
        Paragraph("PayGuard – Audit Report", styles["Title"])
    )

    content.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 18))

    content.append(
        Paragraph("1. Executive Summary", styles["Heading2"])
    )

    summary = [
        ["Measure", "Result"],
        ["Total Transactions", str(total)],
        ["Successful Payments", str(successful)],
        ["Failed Payments", str(failed)],
        ["Pending Payments", str(pending)],
        ["Flagged Transactions", str(flagged)],
        ["High-Risk Transactions", str(high_risk)],
        ["Total Refund Amount", f"{refund_total:,.2f}"]
    ]

    table = Table(summary, colWidths=[230, 180])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    content.append(
        Paragraph("2. High-Priority Review Records", styles["Heading2"])
    )

    review = anomalies[
        anomalies["anomaly_detected"] == 1
    ].sort_values(
        "risk_score",
        ascending=False
    ).head(20)

    columns = [
        "transaction_id",
        "amount",
        "risk_score",
        "risk_level",
        "anomaly_reasons"
    ]

    review = review[columns].fillna("")

    rows = [columns] + review.astype(str).values.tolist()

    review_table = Table(
        rows,
        repeatRows=1,
        colWidths=[85, 65, 60, 65, 390]
    )

    review_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))

    content.append(review_table)
    content.append(Spacer(1, 15))

    content.append(
        Paragraph("3. Interpretation", styles["Heading2"])
    )

    content.append(
        Paragraph(
            f"The dataset contains {total} transactions. "
            f"{flagged} records were flagged for manual investigation, "
            f"including {high_risk} high-risk records. "
            "Flags indicate unusual patterns and do not establish fraud. "
            "The review queue should be examined using the supporting "
            "payment and refund records.",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "Data source: Synthetic PayGuard dataset. "
            "This report is generated for academic demonstration.",
            styles["Italic"]
        )
    )

    doc.build(content)

    return buffer.getvalue()
