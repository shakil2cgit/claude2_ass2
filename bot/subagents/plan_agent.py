"""Plan Subagent: Evaluates the explored PR context and orchestrates reviewer routing."""
from typing import List, Dict
from bot.models import PRContext, ReviewPlan

class PlanSubagent:
    """
    Why it exists:
    Acts as a dispatcher to filter files (e.g. ignore binary assets/lockfiles) and selectively
    assign specialized subagents based on the risk profile of each modified file.
    
    What breaks without it:
    Every specialized reviewer runs on every single file (including docs and lockfiles),
    wasting tokens, causing timeout bottlenecks, and generating irrelevant reviews.
    """
    def run(self, context: PRContext) -> ReviewPlan:
        review_scope: List[str] = []
        skipped_files: Dict[str, str] = {}
        active_subagents: List[str] = []

        for f in context.files:
            file_path = f.file_path
            if file_path.endswith((".md", ".txt", ".png", ".jpg", ".svg", ".lock")):
                skipped_files[file_path] = "Non-executable documentation or asset file; excluded from deep code review."
            else:
                review_scope.append(file_path)

        if any("auth" in p or "security" in p or "secret" in p or "token" in p for p in review_scope):
            active_subagents.append("SecuritySubagent")

        if any("payment" in p or "calc" in p or "logic" in p or "service" in p for p in review_scope):
            active_subagents.append("LogicReviewSubagent")

        # Test coverage subagent is activated whenever any core logic is modified
        if review_scope:
            active_subagents.append("TestCoverageSubagent")

        return ReviewPlan(
            pr_id=context.pr_id,
            review_scope=review_scope,
            skipped_files=skipped_files,
            active_subagents=list(set(active_subagents)),
            rationale=f"Assigned {len(active_subagents)} specialized subagents across {len(review_scope)} target code files."
        )
