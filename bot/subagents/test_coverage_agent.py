"""Test Coverage Review Subagent: Detects untested new functions and mutation paths."""
import re
from typing import List, Set
from bot.models import PRContext, ReviewFinding, FindingCategory, FindingSeverity

class TestCoverageSubagent:
    """
    Why it exists:
    Analyzes differential test coverage, ensuring every new public method or core branch introduced
    in the pull request has corresponding unit tests in the same PR.
    
    What breaks without it:
    Developers introduce new code paths and delete routines without tests; regressions pass undetected,
    eroding codebase reliability.
    """
    def review(self, context: PRContext, target_files: List[str]) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        # Find all test files modified in this PR
        test_files = [f for f in context.files if "test" in f.file_path.lower()]
        test_content = " ".join(["\n".join(f.added_lines) for f in test_files])

        # Extract newly introduced function and method definitions in non-test files
        new_methods: List[tuple] = []
        for f in context.files:
            if "test" in f.file_path.lower() or f.file_path not in target_files:
                continue

            # Check functions that were in removed lines (i.e. pre-existing functions being modified)
            existing_functions: Set[str] = set()
            for line in f.removed_lines:
                clean = line.strip().lstrip("- ")
                match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\(', clean)
                if match:
                    existing_functions.add(match.group(1))

            for idx, line in enumerate(f.added_lines, start=1):
                clean = line.strip().lstrip("+ ")
                match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\(', clean)
                if match:
                    func_name = match.group(1)
                    # If it's a private/dunder method or already existed, don't flag as newly introduced
                    if func_name.startswith("__") or func_name in existing_functions:
                        continue
                    new_methods.append((f.file_path, idx, func_name))

        # Check if new methods have corresponding test coverage
        for file_path, line_no, func_name in new_methods:
            is_tested = (func_name in test_content) or (f"test_{func_name}" in test_content)
            if not is_tested:
                findings.append(ReviewFinding(
                    category=FindingCategory.MISSING_TESTS,
                    severity=FindingSeverity.MUST_FIX,
                    file_path=file_path,
                    line_number=line_no,
                    title=f"Untested Method `{func_name}()` Introduced",
                    description=f"New method `{func_name}` was introduced in `{file_path}` but no corresponding "
                                f"unit tests were added or modified in the PR test suite.",
                    suggestion=f"Add unit tests for `{func_name}()` covering standard execution, invalid inputs, and boundary conditions in `tests/`.",
                    auto_fixable=False,
                    suggested_patch=f"""def test_{func_name}_basic():
    # TODO: Add assertions for {func_name}
    pass"""
                ))

        return findings
