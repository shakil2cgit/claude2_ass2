"""Review Rubric Module: Standardized definitions, rule categories, and ranking hierarchy."""
from typing import Dict, Any
from bot.models import FindingSeverity, FindingCategory

RUBRIC_CRITERIA = {
    FindingCategory.SECURITY: {
        "description": "Checks for vulnerabilities, secrets, insecure deserialization, SQLi, and unsafe execution.",
        "must_fix": [
            "Hardcoded secrets, API keys, tokens, or plaintext credentials",
            "SQL / Command / Template injection vulnerabilities",
            "Unchecked user input executed in sensitive contexts",
            "Insecure cryptographic defaults (e.g., MD5 for passwords, weak PRNG)",
            "Authentication or authorization bypass"
        ],
        "should_fix": [
            "Missing security headers in response generation",
            "Overly broad exception catching swallowing security faults",
            "Verbose error messages leaking internal stack traces"
        ],
        "ignore": [
            "Mock secrets used strictly within test fixtures (e.g., 'test_token_123')",
            "Localhost/127.0.0.1 default URLs in local dev configs"
        ]
    },
    FindingCategory.LOGIC_ERROR: {
        "description": "Checks for algorithm errors, incorrect conditions, off-by-one errors, math defects, and race conditions.",
        "must_fix": [
            "Incorrect formula / math operations altering business outcomes (e.g., adding discount instead of subtracting)",
            "Incorrect boolean conditions causing branch inversion",
            "Off-by-one boundary errors in loops or slices",
            "Unchecked NoneType / null dereference causing crash in happy path",
            "State corruption or broken data invariants"
        ],
        "should_fix": [
            "Sub-optimal data structures causing unnecessary O(N^2) complexity",
            "Redundant calculations inside tight loops",
            "Dead code or unexecutable branches"
        ],
        "ignore": [
            "Micro-optimizations with no measurable impact on throughput",
            "Alternative syntactic expressions that have identical bytecode"
        ]
    },
    FindingCategory.MISSING_TESTS: {
        "description": "Checks for modified or new business logic that lacks unit/integration test coverage.",
        "must_fix": [
            "New public functions/endpoints completely lacking test cases",
            "Modified calculation/decision branching without corresponding test updates",
            "Error-handling branch (e.g. invalid bounds, exception raising) with 0 assertions"
        ],
        "should_fix": [
            "Missing edge case tests (e.g., 0 values, empty string, boundary limits)",
            "Tests lacking docstrings or clear assertions"
        ],
        "ignore": [
            "Pure documentation or comment modifications",
            "Configuration file adjustments without logic change"
        ]
    },
    FindingCategory.STYLE: {
        "description": "Checks for naming conventions, clean code principles, and formatting.",
        "must_fix": [
            "Misleading variable or function names directly obscuring critical business logic"
        ],
        "should_fix": [
            "PEP 8 naming violations (e.g. camelCase for Python functions)",
            "Excessively long functions (> 100 lines) with high cyclomatic complexity",
            "Duplicate code blocks that should be extracted into shared helpers"
        ],
        "ignore": [
            "Minor whitespace, trailing newline, or import sorting (delegated to ruff/black)",
            "Single vs double quote preferences"
        ]
    }
}

def classify_finding(category: FindingCategory, rule_trigger: str) -> FindingSeverity:
    """Helper to classify a finding according to the standardized rubric."""
    rules = RUBRIC_CRITERIA.get(category, {})
    if any(trigger.lower() in rule_trigger.lower() for trigger in rules.get("must_fix", [])):
        return FindingSeverity.MUST_FIX
    if any(trigger.lower() in rule_trigger.lower() for trigger in rules.get("should_fix", [])):
        return FindingSeverity.SHOULD_FIX
    return FindingSeverity.IGNORE
