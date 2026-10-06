from functools import wraps
from flask import request, g
import jwt
from firebase_admin import auth as firebase_auth
from backend.config import Config
from backend.utils.responses import error_response
from backend.repositories.firestore_repository import FirestoreRepository

user_repo = FirestoreRepository("users")

def token_required(f):
    """
    Decorator to authenticate requests via Firebase ID token or internal JWT.
    Verifies token, fetches user from Firestore `users/{uid}`, and assigns to `g.current_user`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return error_response(
                message="Authorization token is required",
                error_code="TOKEN_MISSING",
                status_code=401
            )

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error_response(
                message="Authorization header must be formatted as: Bearer <token>",
                error_code="TOKEN_MALFORMED",
                status_code=401
            )

        token = parts[1]
        user_record = None

        # 1. Attempt verification with Firebase Admin SDK
        try:
            decoded_firebase = firebase_auth.verify_id_token(token)
            uid = decoded_firebase.get("uid")
            email = decoded_firebase.get("email", "")

            # Fetch user from Cloud Firestore 'users/{uid}'
            user_record = user_repo.get_by_id(uid)
            if not user_record:
                # Provision user document in Firestore if not already present
                role = "Administrator" if "admin" in email.lower() else "Staff"
                user_record = user_repo.create({
                    "uid": uid,
                    "id": uid,
                    "email": email,
                    "name": decoded_firebase.get("name") or email.split("@")[0].capitalize(),
                    "role": role,
                    "status": "Active"
                }, doc_id=uid)
        except Exception:
            # 2. Fallback to local JWT verification (for development & test suite)
            try:
                payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("sub") or payload.get("id") or payload.get("uid")
                user_record = user_repo.get_by_id(user_id)
                if not user_record and payload.get("email"):
                    user_record = user_repo.find_one({"email": payload.get("email")})
            except Exception as jwt_err:
                return error_response(
                    message="Invalid or expired authentication token. Please log in again.",
                    error_code="TOKEN_INVALID",
                    status_code=401
                )

        if not user_record:
            return error_response(
                message="User associated with this token was not found in Firestore",
                error_code="USER_NOT_FOUND",
                status_code=401
            )

        if user_record.get("status") == "Inactive":
            return error_response(
                message="User account is deactivated. Please contact administrator",
                error_code="ACCOUNT_INACTIVE",
                status_code=403
            )

        # Store in flask g
        g.current_user = user_record
        return f(*args, **kwargs)

    return decorated


def role_required(*allowed_roles):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Checks user's role stored in Firestore users/{uid}.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                return error_response(
                    message="User session not authenticated",
                    error_code="UNAUTHENTICATED",
                    status_code=401
                )

            user_role = current_user.get("role")
            if user_role not in allowed_roles:
                return error_response(
                    message=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}",
                    error_code="FORBIDDEN",
                    status_code=403
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator
