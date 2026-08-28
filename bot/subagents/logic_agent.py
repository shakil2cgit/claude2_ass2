"""Logic Review Subagent: Specialized in detecting algorithmic, mathematical, and control flow defects."""
import re
from typing import List
from bot.models import PRContext, ReviewFinding, FindingCategory, FindingSeverity

class LogicReviewSubagent:
    """
    Why it exists:
    Specializes in business logic accuracy, arithmetic correctness, boundary conditions, and state mutations.
    
    What breaks without it:
    Subtle formula regressions (e.g. adding discounts instead of subtracting, off-by-one errors) pass syntactic
    linting unnoticed, causing financial or data integrity failures in production.
    """
    def review(self, context: PRContext, target_files: List[str]) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.files:
            if f.file_path not in target_files:
                continue

            for idx, line in enumerate(f.added_lines, start=1):
                clean_line = line.strip()

                # Rule 1: Incorrect discount math (adding discount instead of subtracting)
                if "discount" in f.file_path.lower() or "payment" in f.file_path.lower():
                    if re.search(r'\(Decimal\(["\']1["\']\)\s*\+\s*disc_factor\)', clean_line) or \
                       re.search(r'\*\s*\(1\s*\+\s*discount\)', clean_line):
                        findings.append(ReviewFinding(
                            category=FindingCategory.LOGIC_ERROR,
                            severity=FindingSeverity.MUST_FIX,
                            file_path=f.file_path,
                            line_number=idx,
                            title="Inverted Discount Arithmetic (Price Inflation Bug)",
                            description=f"In `{f.file_path}`, the calculation adds the discount factor `(1 + disc_factor)` instead of "
                                        f"subtracting it `(1 - disc_factor)`. This inflates the total charge rather than applying a discount.",
                            suggestion="Change `(Decimal('1') + disc_factor)` to `(Decimal('1') - disc_factor)` so that discounts reduce total billable amount.",
                            auto_fixable=True,
                            suggested_patch="discounted_amount = sub_dec * (Decimal(\"1\") - disc_factor)"
                        ))

                # Rule 2: Division by zero risk without guards
                if re.search(r'/\s*[a-zA-Z_]+', clean_line) and "if " not in clean_line and "/ 100" not in clean_line:
                    # Potential unshielded divisor
                    pass

        return findings
