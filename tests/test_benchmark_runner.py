"""TDD Tests for Benchmark Evaluation."""
import pytest
from benchmark.evaluate_benchmark import run_benchmark_evaluation

def test_benchmark_catches_all_seeded_defects():
    metrics = run_benchmark_evaluation()
    
    # Check 1: 3 out of 3 seeded defects caught
    assert metrics["caught_defects"] == 3
    assert metrics["total_seeded_defects"] == 3
    assert metrics["recall_percent"] == 100.0
    assert "DEFECT-001-LOGIC" in metrics["matched_defect_ids"]
    assert "DEFECT-002-UNTESTED" in metrics["matched_defect_ids"]
    assert "DEFECT-003-SECURITY" in metrics["matched_defect_ids"]

    # Check 2: 0 false alarms
    assert metrics["false_alarms"] == 0
    assert metrics["precision_percent"] == 100.0
    assert metrics["triage_status"] == "BLOCKED"
