"""User Manager Module for managing user accounts and roles."""
from typing import Dict, Optional, List

class UserManager:
    def __init__(self):
        self._users: Dict[str, Dict[str, str]] = {}

    def register_user(self, username: str, email: str, role: str = "viewer") -> Dict[str, str]:
        """Register a new user with validation."""
        if not username or not email:
            raise ValueError("Username and email are required")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if username in self._users:
            raise ValueError("User already exists")

        user_data = {
            "username": username,
            "email": email,
            "role": role,
            "status": "active"
        }
        self._users[username] = user_data
        return user_data

    def get_user(self, username: str) -> Optional[Dict[str, str]]:
        """Retrieve user by username."""
        return self._users.get(username)

    def list_users_by_role(self, role: str) -> List[Dict[str, str]]:
        """List all users matching a given role."""
        return [u for u in self._users.values() if u["role"] == role]
