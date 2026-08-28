"""Review Bot Orchestrator: Executes multi-subagent pipeline end-to-end."""
import json
from typing import List
from bot.models import PRContext, BotReviewResult, ReviewFinding, FindingSeverity
from bot.subagents.explore_agent import ExploreSubagent
from bot.subagents.plan_agent import PlanSubagent
from bot.subagents.security_agent import SecuritySubagent
from bot.subagents.logic_agent import LogicReviewSubagent
from bot.subagents.test_coverage_agent import TestCoverageSubagent
from bot.subagents.autofix_agent import AutoFixSubagent
from bot.triage import TriageEngine
from bot.context_manager import ContextBudgetManager

class PRReviewOrchestrator:
    def __init__(self):
        self.explore_agent = ExploreSubagent()
        self.plan_agent = PlanSubagent()
        self.security_agent = SecuritySubagent()
        self.logic_agent = LogicReviewSubagent()
        self.test_agent = TestCoverageSubagent()
        self.autofix_agent = AutoFixSubagent()

    def run_review(self, context: PRContext) -> BotReviewResult:
        """Run full subagent review pipeline."""
        # 1. Explore Phase
        context = self.explore_agent.run(context)

        # 2. Plan Phase
        plan = self.plan_agent.run(context)

        # 3. Context Preparation & Routing
        findings: List[ReviewFinding] = []

        if "SecuritySubagent" in plan.active_subagents:
            findings.extend(self.security_agent.review(context, plan.review_scope))

        if "LogicReviewSubagent" in plan.active_subagents:
            findings.extend(self.logic_agent.review(context, plan.review_scope))

        if "TestCoverageSubagent" in plan.active_subagents:
            findings.extend(self.test_agent.review(context, plan.review_scope))

        # 4. Auto-fix Phase
        autofix_patches = self.autofix_agent.generate_patches(findings)

        # 5. Triage Phase
        status, priority, labels = TriageEngine.evaluate(findings)

        must_fix = sum(1 for f in findings if f.severity == FindingSeverity.MUST_FIX)
        should_fix = sum(1 for f in findings if f.severity == FindingSeverity.SHOULD_FIX)
        ignore = sum(1 for f in findings if f.severity == FindingSeverity.IGNORE)

        summary = f"Review completed for PR #{context.pr_id}. Findings: {must_fix} Must-Fix, {should_fix} Should-Fix, {ignore} Ignored. Status: {status} (Priority: {priority})."

        return BotReviewResult(
            pr_id=context.pr_id,
            summary=summary,
            findings=findings,
            must_fix_count=must_fix,
            should_fix_count=should_fix,
            ignore_count=ignore,
            status=status,
            triage_labels=labels,
            auto_fix_patches=autofix_patches
        )

    def generate_markdown_comment(self, result: BotReviewResult) -> str:
        """Generates a rich, structured GitHub PR review comment."""
        status_badge = "🚨 **CHANGES REQUESTED (BLOCKED)**" if result.status == "BLOCKED" else (
            "⚠️ **IMPROVEMENTS SUGGESTED**" if result.status == "NEEDS_WORK" else "✅ **APPROVED**"
        )

        lines = [
            f"## 🤖 AI Subagent PR Review Report",
            f"",
            f"{status_badge}",
            f"",
            f"**Triage Labels**: " + " ".join([f"`{label}`" for label in result.triage_labels]),
            f"",
            f"### 📊 Review Summary",
            f"- **Must-Fix (Blockers)**: {result.must_fix_count}",
            f"- **Should-Fix (Improvements)**: {result.should_fix_count}",
            f"- **Ignored (Non-issues)**: {result.ignore_count}",
            f"",
            f"---",
            f"### 🔍 Detailed Findings",
            f""
        ]

        if not result.findings:
            lines.append("🎉 **No issues found! All checks passed cleanly.**")
        else:
            for i, f in enumerate(result.findings, 1):
                icon = "🔴" if f.severity == FindingSeverity.MUST_FIX else ("🟡" if f.severity == FindingSeverity.SHOULD_FIX else "⚪")
                lines.append(f"#### {icon} Finding #{i}: {f.title} (`{f.severity.value}`)")
                lines.append(f"- **Category**: `{f.category.value}`")
                lines.append(f"- **File**: `{f.file_path}`" + (f" (Line ~{f.line_number})" if f.line_number else ""))
                lines.append(f"- **Description**: {f.description}")
                lines.append(f"- **Actionable Suggestion**: {f.suggestion}")
                if f.suggested_patch:
                    lines.append(f"```python\n# Suggested Resolution\n{f.suggested_patch}\n```")
                lines.append(f"")

        lines.extend([
            f"---",
            f"### 🛠️ Auto-Fix & Remediation Status",
            f"| Finding | Auto-Fixable | Human Approval Required |",
            f"|---|---|---|"
        ])

        for p in result.auto_fix_patches:
            auto_str = "✅ Yes" if p["safety_level"] == "AUTO_APPLY_SAFE" else "❌ No"
            human_str = "⚠️ Yes" if p["requires_human_approval"] else "⚡ No (Autonomous)"
            lines.append(f"| {p['finding_title']} | {auto_str} | {human_str} |")

        lines.append(f"\n_Generated by AI Subagent Review Bot running on GitHub Actions CI_")
        return "\n".join(lines)
