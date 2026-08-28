"""TDD Tests for Context Budget Manager."""
import pytest
from bot.context_manager import ContextBudgetManager
from benchmark.seeded_pr_diff import get_seeded_benchmark_pr

def test_compact_diff_strips_bloat():
    pr = get_seeded_benchmark_pr()
    auth_diff = pr.files[0]
    compacted = ContextBudgetManager.compact_diff(auth_diff)
    
    assert "File: app/auth.py" in compacted
    assert "+ DEFAULT_BACKUP_KEY" in compacted
    assert "- def get_secret_key" in compacted
    # Git header syntax '---' and '@@' stripped
    assert "@@" not in compacted

def test_prepare_agent_payload_budget_limit():
    pr = get_seeded_benchmark_pr()
    payload = ContextBudgetManager.prepare_agent_payload(pr, ["app/auth.py", "app/payment_service.py"])

    assert payload["pr_id"] == 42
    assert "token_estimate" in payload
    assert payload["token_estimate"] <= ContextBudgetManager.PER_AGENT_BUDGET
