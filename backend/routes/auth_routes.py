from flask import Blueprint, request, g
from backend.services.auth_service import AuthService
from backend.utils.responses import success_response, error_response
from backend.utils.decorators import token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint.
    Accepts:
    1. {"idToken": "<FIREBASE_ID_TOKEN>"} (From frontend Firebase Auth)
    2. {"email": "...", "password": "..."} (Direct development / API login)
    """
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken")
    email = data.get("email")
    password = data.get("password")

    result, message, error_code = AuthService.login(email=email, password=password, id_token=id_token)
    if not result:
        return error_response(
            message=message,
            error_code=error_code or "AUTH_FAILED",
            status_code=401
        )

    return success_response(
        data=result,
        message=message,
        status_code=200
    )

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register endpoint for new users.
    Accepts:
    {"name": "...", "email": "...", "password": "...", "role": "Staff", "username": "...", "phone": "..."}
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "Staff")
    username = data.get("username", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not email or not password:
        return error_response(
            message="Full name, email address, and password are required.",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    if len(password) < 6:
        return error_response(
            message="Password must be at least 6 characters long.",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

    user, error_msg = AuthService.register_user({
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "username": username,
        "phone": phone
    })

    if not user:
        return error_response(
            message=error_msg or "Failed to register new user.",
            error_code="REGISTRATION_FAILED",
            status_code=400
        )

    token = AuthService.generate_token(user)
    return success_response(
        data={
            "token": token,
            "user": user
        },
        message="Account created successfully! Welcome to Garment Tracker.",
        status_code=201
    )

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me():
    user = AuthService.get_user_by_id(g.current_user.get("uid") or g.current_user.get("id"))
    if not user:
        return error_response("User not found", "NOT_FOUND", 404)
    return success_response(data=user, message="Authenticated user profile retrieved")

@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    return success_response(message="Logged out successfully.")
