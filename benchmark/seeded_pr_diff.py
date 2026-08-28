"""Seeded Defect PR Diff Generator: Simulates a real Pull Request containing the 3 seeded defects."""
from bot.models import PRContext, PRFileDiff

def get_seeded_benchmark_pr() -> PRContext:
    """Returns a realistic PRContext representing PR #42 containing the 3 seeded defects."""
    auth_diff = PRFileDiff(
        file_path="app/auth.py",
        status="modified",
        added_lines=[
            "+DEFAULT_BACKUP_KEY = \"mock_secret_key_994829384729103948572910\"",
            "+def get_secret_key() -> str:",
            "+    key = os.environ.get(SECRET_KEY_ENV, DEFAULT_BACKUP_KEY)",
            "+    return key"
        ],
        removed_lines=[
            "-def get_secret_key() -> str:",
            "-    key = os.environ.get(SECRET_KEY_ENV)",
            "-    if not key:",
            "-        raise ValueError(f\"Missing required environment variable: {SECRET_KEY_ENV}\")",
            "-    return key"
        ],
        patch="""--- a/app/auth.py
+++ b/app/auth.py
@@ -5,9 +5,6 @@
 SECRET_KEY_ENV = "APP_SECRET_KEY"
+DEFAULT_BACKUP_KEY = "mock_secret_key_994829384729103948572910"
 
 def get_secret_key() -> str:
-    key = os.environ.get(SECRET_KEY_ENV)
-    if not key:
-        raise ValueError(f"Missing required environment variable: {SECRET_KEY_ENV}")
-    return key
+    key = os.environ.get(SECRET_KEY_ENV, DEFAULT_BACKUP_KEY)
+    return key
"""
    )

    payment_diff = PRFileDiff(
        file_path="app/payment_service.py",
        status="modified",
        added_lines=[
            "+        # Apply discount factor",
            "+        discounted_amount = sub_dec * (Decimal(\"1\") + disc_factor)"
        ],
        removed_lines=[
            "-        discounted_amount = sub_dec * (Decimal(\"1\") - disc_factor)"
        ],
        patch="""--- a/app/payment_service.py
+++ b/app/payment_service.py
@@ -16,3 +16,4 @@
         sub_dec = Decimal(str(subtotal))
         disc_factor = Decimal(str(discount_percent)) / Decimal("100")
-        discounted_amount = sub_dec * (Decimal("1") - disc_factor)
+        # Apply discount factor
+        discounted_amount = sub_dec * (Decimal("1") + disc_factor)
"""
    )

    user_diff = PRFileDiff(
        file_path="app/user_manager.py",
        status="modified",
        added_lines=[
            "+    def delete_user(self, username: str, force: bool = False) -> bool:",
            "+        \"\"\"Delete a user by username.\"\"\"",
            "+        if username in self._users:",
            "+            del self._users[username]",
            "+            return True",
            "+        return False"
        ],
        removed_lines=[],
        patch="""--- a/app/user_manager.py
+++ b/app/user_manager.py
@@ -28,3 +28,9 @@
     def list_users_by_role(self, role: str) -> List[Dict[str, str]]:
         return [u for u in self._users.values() if u["role"] == role]
+
+    def delete_user(self, username: str, force: bool = False) -> bool:
+        \"\"\"Delete a user by username.\"\"\"
+        if username in self._users:
+            del self._users[username]
+            return True
+        return False
"""
    )

    return PRContext(
        pr_id=42,
        title="feat: Add user deletion, adjust discount calculation and add fallback secret",
        description="This PR adds user deletion endpoint, updates payment calculation logic, and provides fallback secret for dev environment.",
        author="contributor-bob",
        target_branch="main",
        source_branch="feature/user-deletion-and-discounts",
        files=[auth_diff, payment_diff, user_diff]
    )

def get_clean_benchmark_pr() -> PRContext:
    """Returns a PRContext representing a clean, high-quality PR with 0 defects."""
    doc_diff = PRFileDiff(
        file_path="README.md",
        status="modified",
        added_lines=[
            "+## Deployment Guide",
            "+To run the microservice in production, ensure `APP_SECRET_KEY` is configured."
        ],
        removed_lines=[],
        patch="""--- a/README.md
+++ b/README.md
@@ -10,2 +10,4 @@
+## Deployment Guide
+To run the microservice in production, ensure `APP_SECRET_KEY` is configured.
"""
    )
    return PRContext(
        pr_id=43,
        title="docs: Update deployment instructions in README",
        description="Added production deployment configuration section to README.",
        author="dev-alice",
        target_branch="main",
        source_branch="docs/deployment-guide",
        files=[doc_diff]
    )
