"""Payment calculation and transaction service."""
from decimal import Decimal
from typing import Dict, Any

class PaymentService:
    def __init__(self, tax_rate: float = 0.05):
        self.tax_rate = Decimal(str(tax_rate))

    def calculate_total(self, subtotal: float, discount_percent: float = 0.0) -> float:
        """
        Calculate final price including discount and tax.
        Formula: Total = (Subtotal - DiscountAmount) * (1 + TaxRate)
        """
        if subtotal < 0:
            raise ValueError("Subtotal cannot be negative")
        if not (0 <= discount_percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100")

        sub_dec = Decimal(str(subtotal))
        disc_factor = Decimal(str(discount_percent)) / Decimal("100")
        discounted_amount = sub_dec * (Decimal("1") - disc_factor)
        total = discounted_amount * (Decimal("1") + self.tax_rate)
        return float(round(total, 2))

    def process_refund(self, original_amount: float, refund_amount: float) -> Dict[str, Any]:
        """Process refund with strict bounds checks."""
        if refund_amount <= 0:
            raise ValueError("Refund amount must be positive")
        if refund_amount > original_amount:
            raise ValueError("Refund amount cannot exceed original amount")
        return {
            "status": "APPROVED",
            "refunded": refund_amount,
            "balance_retained": round(original_amount - refund_amount, 2)
        }
