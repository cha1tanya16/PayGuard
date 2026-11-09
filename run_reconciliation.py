
from modules.reconciliation import reconcile_payments

ledger = reconcile_payments()

print("\nSample reconciled transactions:")
print(
    ledger[
        [
            "transaction_id",
            "amount",
            "final_payment_status",
            "total_attempts",
            "total_refund",
            "net_amount",
            "refund_classification",
            "review_required"
        ]
    ].head(10).to_string(index=False)
)
