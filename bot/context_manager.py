"""Context Management Module: Manages token budgeting, diff compaction, and structured subagent handoffs."""
from typing import Dict, Any, List
from bot.models import PRContext, PRFileDiff

class ContextBudgetManager:
    """
    Manages context window limits by:
    1. Compacting raw git diffs into high-density semantic representations.
    2. Enforcing per-subagent token ceilings (e.g., max 1500 tokens per subagent payload).
    3. Truncating non-essential metadata and stripping unmodified context padding.
    """
    MAX_TOTAL_BUDGET = 8000
    PER_AGENT_BUDGET = 2000

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation: ~4 chars per token."""
        return max(1, len(text) // 4)

    @classmethod
    def compact_diff(cls, file_diff: PRFileDiff) -> str:
        """
        Compacts diffs by:
        - Removing unchanged context lines and git index markers.
        - Highlighting only added (+) and removed (-) meaningful lines.
        """
        compact_lines = []
        for line in file_diff.added_lines:
            compact_lines.append(f"+ {line.strip('+ ').strip()}")
        for line in file_diff.removed_lines:
            compact_lines.append(f"- {line.strip('- ').strip()}")

        compacted = "\n".join(compact_lines)
        return f"File: {file_diff.file_path} ({file_diff.status})\n{compacted}"

    @classmethod
    def prepare_agent_payload(cls, pr_context: PRContext, target_files: List[str]) -> Dict[str, Any]:
        """Prepares a compacted, budgeted payload for an individual subagent."""
        selected_diffs = [
            cls.compact_diff(f) for f in pr_context.files if f.file_path in target_files
        ]
        compacted_body = "\n\n".join(selected_diffs)
        token_count = cls.estimate_tokens(compacted_body)

        # Truncation safety guard if budget exceeded
        if token_count > cls.PER_AGENT_BUDGET:
            char_limit = cls.PER_AGENT_BUDGET * 4
            compacted_body = compacted_body[:char_limit] + "\n...[TRUNCATED TO FIT CONTEXT BUDGET]..."

        return {
            "pr_id": pr_context.pr_id,
            "pr_title": pr_context.title,
            "explored_summary": pr_context.explored_summary or "",
            "diff_payload": compacted_body,
            "token_estimate": cls.estimate_tokens(compacted_body)
        }
