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
