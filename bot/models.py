"""Pydantic data models for the AI PR Reviewer Bot system."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FindingSeverity(str, Enum):
    MUST_FIX = "must-fix"       # Blocker: Bugs, security vulnerabilities, regression, test holes in critical logic
    SHOULD_FIX = "should-fix"   # Important: Performance debt, maintainability, missing edge tests, minor smell
    IGNORE = "ignore"           # Cosmetic: Trivial style preferences, formatting already handled by linter

class FindingCategory(str, Enum):
    LOGIC_ERROR = "logic_error"
    MISSING_TESTS = "missing_tests"
    SECURITY = "security"
    STYLE = "style"

class ReviewFinding(BaseModel):
    category: FindingCategory
    severity: FindingSeverity
    file_path: str
    line_number: Optional[int] = None
    title: str
    description: str
    suggestion: str
    auto_fixable: bool = False
    suggested_patch: Optional[str] = None

class PRFileDiff(BaseModel):
    file_path: str
    old_path: Optional[str] = None
    status: str = "modified" # added, modified, deleted
    added_lines: List[str] = Field(default_factory=list)
    removed_lines: List[str] = Field(default_factory=list)
    patch: str = ""

class PRContext(BaseModel):
    pr_id: int
    title: str
    description: str
    author: str
    target_branch: str = "main"
    source_branch: str = "feature/update"
    files: List[PRFileDiff] = Field(default_factory=list)
    explored_summary: Optional[str] = None
    changed_components: List[str] = Field(default_factory=list)
    raw_token_count_estimate: int = 0
    compacted_token_count_estimate: int = 0

class ReviewPlan(BaseModel):
    pr_id: int
    review_scope: List[str] = Field(default_factory=list)
    skipped_files: Dict[str, str] = Field(default_factory=dict)
    active_subagents: List[str] = Field(default_factory=list)
    rationale: str = ""

class BotReviewResult(BaseModel):
    pr_id: int
    summary: str
    findings: List[ReviewFinding] = Field(default_factory=list)
    must_fix_count: int = 0
    should_fix_count: int = 0
    ignore_count: int = 0
    status: str = "NEEDS_WORK" # APPROVED, NEEDS_WORK, BLOCKED
    triage_labels: List[str] = Field(default_factory=list)
    auto_fix_patches: List[Dict[str, Any]] = Field(default_factory=list)
