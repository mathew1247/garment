from flask import Blueprint, request
from backend.services.auth_service import AuthService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.decorators import token_required, role_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

@user_bp.route("", methods=["GET"])
@token_required
@role_required("Administrator")
def get_all_users():
    users = AuthService.get_all_users()
    return list_response(data=users, count=len(users), message="Users retrieved successfully")

@user_bp.route("/<user_id>", methods=["GET"])
@token_required
@role_required("Administrator")
def get_user(user_id):
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return error_response("User not found", "NOT_FOUND", 404)
    return success_response(data=user, message="User retrieved successfully")

@user_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator")
def create_user():
    data = request.get_json(silent=True) or {}
    if not data.get("email") or not data.get("name"):
        return error_response("Email and name are required", "VALIDATION_ERROR", 400)

    user, err = AuthService.create_user(data)
    if err:
        return error_response(err, "DUPLICATE_USER", 409)

    return success_response(data=user, message="User created successfully", status_code=201)

@user_bp.route("/<user_id>", methods=["PUT"])
@token_required
@role_required("Administrator")
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    user, err = AuthService.update_user(user_id, data)
    if err:
        return error_response(err, "UPDATE_FAILED", 400)
    return success_response(data=user, message="User updated successfully")

@user_bp.route("/<user_id>", methods=["DELETE"])
@token_required
@role_required("Administrator")
def delete_user(user_id):
    success, err = AuthService.delete_user(user_id)
    if not success:
        return error_response(err or "User not found", "DELETE_FAILED", 404)
    return success_response(message="User deleted successfully")
