"""TDD Tests for Auto-fix and Triage Systems."""
import pytest
from bot.orchestrator import PRReviewOrchestrator
from benchmark.seeded_pr_diff import get_seeded_benchmark_pr, get_clean_benchmark_pr

def test_orchestrator_benchmark_pr_triage():
    orchestrator = PRReviewOrchestrator()
    pr = get_seeded_benchmark_pr()
    result = orchestrator.run_review(pr)

    assert result.status == "BLOCKED"
    assert result.must_fix_count == 3
    assert "security-blocker" in result.triage_labels
    assert "logic-error" in result.triage_labels
    assert "needs-tests" in result.triage_labels
    assert "do-not-merge" in result.triage_labels
    assert len(result.auto_fix_patches) == 3

    # Check auto-apply safety status
    sec_patch = next(p for p in result.auto_fix_patches if p["category"] == "security")
    assert sec_patch["safety_level"] == "AUTO_APPLY_SAFE"
    assert sec_patch["requires_human_approval"] is False

    test_patch = next(p for p in result.auto_fix_patches if p["category"] == "missing_tests")
    assert test_patch["safety_level"] == "MANUAL_REVIEW_REQUIRED"
    assert test_patch["requires_human_approval"] is True

def test_orchestrator_clean_pr_approval():
    orchestrator = PRReviewOrchestrator()
    clean_pr = get_clean_benchmark_pr()
    result = orchestrator.run_review(clean_pr)

    assert result.status == "APPROVED"
    assert result.must_fix_count == 0
    assert "bot-approved" in result.triage_labels
    assert "ready-to-merge" in result.triage_labels
