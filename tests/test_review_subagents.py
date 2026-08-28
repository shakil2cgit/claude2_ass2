"""TDD Tests for Review Subagents (Security, Logic, Test Coverage)."""
import pytest
from bot.models import FindingCategory, FindingSeverity
from bot.subagents.security_agent import SecuritySubagent
from bot.subagents.logic_agent import LogicReviewSubagent
from bot.subagents.test_coverage_agent import TestCoverageSubagent
from benchmark.seeded_pr_diff import get_seeded_benchmark_pr, get_clean_benchmark_pr

def test_security_subagent_detects_secret():
    agent = SecuritySubagent()
    pr = get_seeded_benchmark_pr()
    findings = agent.review(pr, ["app/auth.py", "app/payment_service.py", "app/user_manager.py"])

    assert len(findings) == 1
    f = findings[0]
    assert f.category == FindingCategory.SECURITY
    assert f.severity == FindingSeverity.MUST_FIX
    assert "Hardcoded" in f.title
    assert "app/auth.py" in f.file_path

def test_logic_subagent_detects_inverted_discount():
    agent = LogicReviewSubagent()
    pr = get_seeded_benchmark_pr()
    findings = agent.review(pr, ["app/auth.py", "app/payment_service.py", "app/user_manager.py"])

    assert len(findings) == 1
    f = findings[0]
    assert f.category == FindingCategory.LOGIC_ERROR
    assert f.severity == FindingSeverity.MUST_FIX
    assert "Discount" in f.title
    assert "app/payment_service.py" in f.file_path

def test_test_coverage_subagent_detects_untested_method():
    agent = TestCoverageSubagent()
    pr = get_seeded_benchmark_pr()
    findings = agent.review(pr, ["app/auth.py", "app/payment_service.py", "app/user_manager.py"])

    assert len(findings) == 1
    f = findings[0]
    assert f.category == FindingCategory.MISSING_TESTS
    assert f.severity == FindingSeverity.MUST_FIX
    assert "delete_user" in f.title
    assert "app/user_manager.py" in f.file_path

def test_clean_pr_produces_zero_findings():
    sec_agent = SecuritySubagent()
    log_agent = LogicReviewSubagent()
    test_agent = TestCoverageSubagent()
    
    clean_pr = get_clean_benchmark_pr()
    scope = ["README.md"]

    assert len(sec_agent.review(clean_pr, scope)) == 0
    assert len(log_agent.review(clean_pr, scope)) == 0
    assert len(test_agent.review(clean_pr, scope)) == 0
