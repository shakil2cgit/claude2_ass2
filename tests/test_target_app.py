"""Unit tests for target repository microservice."""
import os
import pytest
from app.auth import generate_signature, verify_token, get_secret_key
from app.payment_service import PaymentService
from app.user_manager import UserManager

def test_auth_signature_and_verification(monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "super-secure-production-key-12345")
    key = get_secret_key()
    sig = generate_signature("user-session-99", key)
    assert verify_token(sig, sig) is True
    assert verify_token("tampered-signature", sig) is False
    assert verify_token("", sig) is False

def test_payment_calculation():
    service = PaymentService(tax_rate=0.10)
    # $100 with 20% discount = $80 + 10% tax = $88.00
    assert service.calculate_total(100.0, 20.0) == 88.00
    # $50 with 0% discount = $50 + 10% tax = $55.00
    assert service.calculate_total(50.0, 0.0) == 55.00

def test_payment_refund():
    service = PaymentService()
    result = service.process_refund(100.0, 30.0)
    assert result["status"] == "APPROVED"
    assert result["refunded"] == 30.0
    assert result["balance_retained"] == 70.0

    with pytest.raises(ValueError):
        service.process_refund(100.0, 150.0)

def test_user_manager_crud():
    manager = UserManager()
    user = manager.register_user("alice", "alice@example.com", "admin")
    assert user["username"] == "alice"
    assert manager.get_user("alice") is not None
    assert len(manager.list_users_by_role("admin")) == 1

    with pytest.raises(ValueError):
        manager.register_user("bob", "invalid-email")
