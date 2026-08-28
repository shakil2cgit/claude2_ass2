"""TDD Tests for Explore Subagent."""
import pytest
from bot.subagents.explore_agent import ExploreSubagent
from benchmark.seeded_pr_diff import get_seeded_benchmark_pr, get_clean_benchmark_pr

def test_explore_subagent_summarization():
    agent = ExploreSubagent()
    pr = get_seeded_benchmark_pr()
    
    assert pr.explored_summary is None
    result = agent.run(pr)

    assert result.explored_summary is not None
    assert "PR #42 Overview" in result.explored_summary
    assert "Payment & Billing Engine" in result.changed_components
    assert "Authentication & Security Layer" in result.changed_components
    assert "User Domain & Identity" in result.changed_components
    assert result.compacted_token_count_estimate > 0

def test_explore_subagent_clean_pr():
    agent = ExploreSubagent()
    clean_pr = get_clean_benchmark_pr()
    result = agent.run(clean_pr)
    
    assert "Documentation / Configuration" in result.changed_components
    assert "README.md" in result.explored_summary
