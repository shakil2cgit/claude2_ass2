"""Auto-fix Subagent: Generates safe git patches for deterministic issues."""
from typing import List, Dict, Any
from bot.models import ReviewFinding, FindingCategory

class AutoFixSubagent:
    """
    Automated Remediation Engine:
    
    Safe Autonomous Execution (No Human Approval Needed):
    - Automated lint formatting
    - Removing hardcoded secret and replacing with environment variable call
    - Math inversion bug fixes where ground truth formula is unambiguous
    
    Requires Human-in-the-Loop Approval:
    - Designing and generating brand new test logic assertions
    - Database schema alterations or architectural rewrites
    - Destructive state mutations
    """
    def generate_patches(self, findings: List[ReviewFinding]) -> List[Dict[str, Any]]:
        patches: List[Dict[str, Any]] = []

        for finding in findings:
            if finding.auto_fixable and finding.suggested_patch:
                patches.append({
                    "file_path": finding.file_path,
                    "finding_title": finding.title,
                    "category": finding.category.value,
                    "target_line": finding.line_number,
                    "replacement_content": finding.suggested_patch,
                    "safety_level": "AUTO_APPLY_SAFE",
                    "requires_human_approval": False
                })
            else:
                patches.append({
                    "file_path": finding.file_path,
                    "finding_title": finding.title,
                    "category": finding.category.value,
                    "target_line": finding.line_number,
                    "replacement_content": finding.suggested_patch or "",
                    "safety_level": "MANUAL_REVIEW_REQUIRED",
                    "requires_human_approval": True
                })

        return patches
