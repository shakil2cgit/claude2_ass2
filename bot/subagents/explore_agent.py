"""Explore Subagent: Inspects changed files, produces compact semantic summary of changes."""
from typing import List
from bot.models import PRContext

class ExploreSubagent:
    """
    Why it exists:
    Dissects raw pull request diffs and generates an abstracted, high-level summary of
    architectural changes, impacted components, and intent.
    
    What breaks without it:
    Downstream review agents get flooded with raw file contents and irrelevant syntax noise,
    exhausting the token budget and losing the macro-context of the pull request.
    """
    def run(self, context: PRContext) -> PRContext:
        """Analyze PR files and attach high-level summary to context."""
        impacted_components: List[str] = []
        summary_points: List[str] = []

        for f in context.files:
            file_name = f.file_path
            added_count = len(f.added_lines)
            removed_count = len(f.removed_lines)

            if "auth" in file_name:
                impacted_components.append("Authentication & Security Layer")
                summary_points.append(f"- `{file_name}`: Modified secret resolution / token handling (+{added_count}, -{removed_count} lines).")
            elif "payment" in file_name:
                impacted_components.append("Payment & Billing Engine")
                summary_points.append(f"- `{file_name}`: Modified monetary calculation / discounting (+{added_count}, -{removed_count} lines).")
            elif "user" in file_name:
                impacted_components.append("User Domain & Identity")
                summary_points.append(f"- `{file_name}`: Modified user lifecycle and account operations (+{added_count}, -{removed_count} lines).")
            elif "test" in file_name:
                impacted_components.append("Test Suite")
                summary_points.append(f"- `{file_name}`: Updated unit / integration tests (+{added_count}, -{removed_count} lines).")
            else:
                impacted_components.append("Documentation / Configuration")
                summary_points.append(f"- `{file_name}`: Updated auxiliary docs/configs (+{added_count}, -{removed_count} lines).")

        raw_size = sum(len(f.patch) for f in context.files)
        context.raw_token_count_estimate = max(1, raw_size // 4)

        explored_text = (
            f"PR #{context.pr_id} Overview:\n"
            f"Title: {context.title}\n"
            f"Author: {context.author}\n"
            f"Impacted Areas: {', '.join(set(impacted_components))}\n"
            f"Change Summary:\n" + "\n".join(summary_points)
        )

        context.explored_summary = explored_text
        context.changed_components = list(set(impacted_components))
        context.compacted_token_count_estimate = max(1, len(explored_text) // 4)

        return context
