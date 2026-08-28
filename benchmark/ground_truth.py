"""Ground Truth Benchmark Definitions: Exactly defines the 3 seeded defects."""
from typing import List, Dict, Any
from bot.models import FindingCategory, FindingSeverity

SEEDED_DEFECTS: List[Dict[str, Any]] = [
    {
        "id": "DEFECT-001-LOGIC",
        "category": FindingCategory.LOGIC_ERROR,
        "expected_severity": FindingSeverity.MUST_FIX,
        "file_path": "app/payment_service.py",
        "target_symbol": "PaymentService.calculate_total",
        "description": "Logic Bug: Discount is added instead of subtracted in price calculation ((1 + disc_factor) instead of (1 - disc_factor)).",
        "keywords": ["discount", "add", "subtract", "calculate_total", "formula", "sign"]
    },
    {
        "id": "DEFECT-002-UNTESTED",
        "category": FindingCategory.MISSING_TESTS,
        "expected_severity": FindingSeverity.MUST_FIX,
        "file_path": "app/user_manager.py",
        "target_symbol": "UserManager.delete_user",
        "description": "Untested Code Path: Added new delete_user method without adding any unit test coverage.",
        "keywords": ["delete_user", "test", "coverage", "untested", "missing test"]
    },
    {
        "id": "DEFECT-003-SECURITY",
        "category": FindingCategory.SECURITY,
        "expected_severity": FindingSeverity.MUST_FIX,
        "file_path": "app/auth.py",
        "target_symbol": "get_secret_key / DEFAULT_BACKUP_KEY",
        "description": "Security Vulnerability: Hardcoded live API secret key token committed as fallback in source code.",
        "keywords": ["hardcoded", "secret", "sk_live", "token", "credential", "api key"]
    }
]
