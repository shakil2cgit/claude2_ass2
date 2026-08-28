"""Triage and Labeling Engine: Assigns GitHub labels, reviewer priority, and merge block status."""
from typing import List, Tuple
from bot.models import ReviewFinding, FindingSeverity, FindingCategory

class TriageEngine:
    """
    Evaluates findings and determines:
    1. GitHub PR labels (e.g. 'security-blocker', 'needs-tests', 'logic-bug', 'ready-to-merge')
    2. Overall PR status ('APPROVED', 'NEEDS_WORK', 'BLOCKED')
    3. Reviewer Priority ('P0-URGENT', 'P1-HIGH', 'P2-MEDIUM', 'P3-LOW')
    """
    @staticmethod
    def evaluate(findings: List[ReviewFinding]) -> Tuple[str, str, List[str]]:
        labels: List[str] = []
        must_fix_count = sum(1 for f in findings if f.severity == FindingSeverity.MUST_FIX)
        should_fix_count = sum(1 for f in findings if f.severity == FindingSeverity.SHOULD_FIX)

        has_security = any(f.category == FindingCategory.SECURITY and f.severity == FindingSeverity.MUST_FIX for f in findings)
        has_logic = any(f.category == FindingCategory.LOGIC_ERROR and f.severity == FindingSeverity.MUST_FIX for f in findings)
        has_missing_tests = any(f.category == FindingCategory.MISSING_TESTS and f.severity == FindingSeverity.MUST_FIX for f in findings)

        if has_security:
            labels.append("security-blocker")
            labels.append("security-team-review-required")
        if has_logic:
            labels.append("logic-error")
        if has_missing_tests:
            labels.append("needs-tests")

        if must_fix_count > 0:
            status = "BLOCKED"
            priority = "P0-URGENT" if has_security else "P1-HIGH"
            labels.append("do-not-merge")
        elif should_fix_count > 0:
            status = "NEEDS_WORK"
            priority = "P2-MEDIUM"
            labels.append("improvements-requested")
        else:
            status = "APPROVED"
            priority = "P3-LOW"
            labels.append("bot-approved")
            labels.append("ready-to-merge")

        return status, priority, labels
