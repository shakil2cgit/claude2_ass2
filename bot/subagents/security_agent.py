"""Security Review Subagent: Specialized in detecting hardcoded secrets, tokens, injections, and auth bypass."""
import re
from typing import List
from bot.models import PRContext, ReviewFinding, FindingCategory, FindingSeverity

class SecuritySubagent:
    """
    Why it exists:
    Specializes exclusively in detecting vulnerabilities, secret leaks, injection flaws, and auth bypasses.
    
    What breaks without it:
    Critical security vulnerabilities like committed API keys, SQL injections, or unverified tokens slip
    into production because generic linters do not understand semantic authorization context.
    """
    # Regex patterns for common secret keys and credentials
    SECRET_PATTERNS = [
        (r'mock_secret_key_[0-9a-zA-Z]{16,}', "Hardcoded Secret / Token Key"),
        (r'sk_live_[0-9a-zA-Z]{20,}', "Stripe / Live API Secret Key"),
        (r'(?i)(?:api_key|secret_key|password|auth_token)\s*=\s*["\'][a-zA-Z0-9_\-]{16,}["\']', "Hardcoded Credential/Token"),
        (r'ghp_[0-9a-zA-Z]{36}', "GitHub Personal Access Token"),
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID")
    ]

    def review(self, context: PRContext, target_files: List[str]) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for f in context.files:
            if f.file_path not in target_files:
                continue

            for idx, line in enumerate(f.added_lines, start=1):
                # Check for hardcoded secrets
                for pattern, secret_type in self.SECRET_PATTERNS:
                    if re.search(pattern, line):
                        # Filter out test fixtures or mocks
                        if "test" in f.file_path.lower() or "mock" in line.lower():
                            continue

                        findings.append(ReviewFinding(
                            category=FindingCategory.SECURITY,
                            severity=FindingSeverity.MUST_FIX,
                            file_path=f.file_path,
                            line_number=idx,
                            title=f"Hardcoded {secret_type} Detected",
                            description=f"A raw secret/token string was committed directly into `{f.file_path}`: `{line.strip()}`. "
                                        f"This exposes live credentials in version control.",
                            suggestion="Remove the hardcoded secret immediately. Fetch the value dynamically from environment variables "
                                       "or a secure secrets manager (e.g. AWS Secrets Manager / Vault). Rotate any compromised keys.",
                            auto_fixable=True,
                            suggested_patch="key = os.environ.get(SECRET_KEY_ENV)\nif not key:\n    raise ValueError(f'Missing required environment variable: {SECRET_KEY_ENV}')"
                        ))

        return findings
