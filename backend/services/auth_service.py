from datetime import datetime, timezone, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_admin import auth as firebase_auth
from backend.config import Config
from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp

user_repo = FirestoreRepository("users")

class AuthService:
    @staticmethod
    def generate_token(user):
        """Generate JWT token valid for the configured duration."""
        now = datetime.now(timezone.utc)
        uid = user.get("uid") or user.get("id")
        payload = {
            "sub": uid,
            "uid": uid,
            "id": uid,
            "email": user.get("email"),
            "name": user.get("name"),
            "role": user.get("role", "Staff"),
            "iat": now,
            "exp": now + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    @classmethod
    def verify_firebase_id_token(cls, id_token):
        """Verify Firebase Authentication ID token sent from frontend."""
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded.get("uid")
            email = decoded.get("email", "")

            user = user_repo.get_by_id(uid)
            if not user:
                role = "Administrator" if "admin" in email.lower() else "Staff"
                user = user_repo.create({
                    "uid": uid,
                    "id": uid,
                    "name": decoded.get("name") or email.split("@")[0].capitalize(),
                    "email": email,
                    "role": role,
                    "status": "Active",
                    "lastLogin": get_current_timestamp()
                }, doc_id=uid)
            else:
                user_repo.update(uid, {"lastLogin": get_current_timestamp()})

            AuditService.log(
                user_id=uid,
                user_name=user.get("name"),
                action="USER_LOGIN",
                entity_type="users",
                entity_id=uid,
                description=f"User {user.get('email')} logged in with Firebase ID token."
            )

            # Return session token and user info
            session_token = cls.generate_token(user)
            sanitized = {k: v for k, v in user.items() if k != "password"}
            return {
                "token": session_token,
                "firebaseToken": id_token,
                "user": sanitized
            }, "Firebase authentication successful", None
        except Exception as e:
            return None, f"Firebase token verification failed: {str(e)}", "INVALID_FIREBASE_TOKEN"

    @classmethod
    def login(cls, email, password=None, id_token=None):
        """
        Authenticate user:
        1. If id_token provided, verify with Firebase Admin SDK.
        2. Otherwise, check Firestore users collection credentials.
        """
        if id_token:
            return cls.verify_firebase_id_token(id_token)

        if not email or not password:
            return None, "Email and password are required", "INVALID_CREDENTIALS"

        user = user_repo.find_one({"email": email.strip()})
        if not user:
            return None, "Invalid email or password", "INVALID_CREDENTIALS"

        stored_password_hash = user.get("password")
        if not stored_password_hash or not check_password_hash(stored_password_hash, password):
            return None, "Invalid email or password", "INVALID_CREDENTIALS"

        if user.get("status") == "Inactive":
            return None, "User account is deactivated. Please contact administrator", "ACCOUNT_DEACTIVATED"

        uid = user.get("uid") or user.get("id")
        user_repo.update(uid, {"lastLogin": get_current_timestamp()})

        AuditService.log(
            user_id=uid,
            user_name=user.get("name"),
            action="USER_LOGIN",
            entity_type="users",
            entity_id=uid,
            description=f"User {user.get('email')} logged in successfully."
        )

        token = cls.generate_token(user)
        sanitized = {k: v for k, v in user.items() if k != "password"}
        return {
            "token": token,
            "user": sanitized
        }, "Login successful", None

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user profile sanitized."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return None
        return {k: v for k, v in user.items() if k != "password"}

    @staticmethod
    def get_all_users():
        """Retrieve all users without password hashes."""
        users = user_repo.get_all(sort_by="name")
        return [{k: v for k, v in u.items() if k != "password"} for u in users]

    @staticmethod
    def create_user(data):
        """Create new user account in Firestore."""
        email = data.get("email", "").strip()
        existing = user_repo.find_one({"email": email})
        if existing:
            return None, "User with this email already exists"

        plain_pwd = data.get("password", "Garment@123")
        uid = data.get("uid")
        user_record = {
            "name": data.get("name", "").strip(),
            "email": email,
            "password": generate_password_hash(plain_pwd),
            "role": data.get("role", "Staff"),
            "status": data.get("status", "Active"),
            "phone": data.get("phone", ""),
            "profileImage": data.get("profileImage", ""),
            "lastLogin": None
        }
        if uid:
            user_record["uid"] = uid
            user_record["id"] = uid

        created = user_repo.create(user_record, doc_id=uid)
        return {k: v for k, v in created.items() if k != "password"}, None

    @staticmethod
    def update_user(user_id, data):
        """Update existing user."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return None, "User not found"

        update_dict = {}
        for field in ["name", "role", "status", "phone", "profileImage"]:
            if field in data:
                update_dict[field] = data[field]

        if "password" in data and data["password"]:
            update_dict["password"] = generate_password_hash(data["password"])

        if "email" in data and data["email"] != user.get("email"):
            existing = user_repo.find_one({"email": data["email"]})
            if existing and existing.get("id") != user_id and existing.get("uid") != user_id:
                return None, "Email is already taken by another user"
            update_dict["email"] = data["email"].strip()

        updated = user_repo.update(user_id, update_dict)
        return {k: v for k, v in updated.items() if k != "password"}, None

    @staticmethod
    def delete_user(user_id):
        """Delete user account."""
        user = user_repo.get_by_id(user_id)
        if not user:
            return False, "User not found"
        user_repo.delete(user_id)
        return True, None
