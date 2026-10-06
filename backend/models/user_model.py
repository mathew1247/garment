class UserModel:
    """User data representation."""
    @staticmethod
    def to_dict(user_id, name, email, password_hash, role="Staff", status="Active", created_at=None, updated_at=None):
        return {
            "id": user_id,
            "name": name,
            "email": email,
            "password": password_hash,
            "role": role,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at
        }

    @staticmethod
    def sanitize(user_dict):
        """Remove sensitive fields like password before sending in API responses."""
        if not user_dict:
            return None
        sanitized = {k: v for k, v in user_dict.items() if k != "password"}
        return sanitized
