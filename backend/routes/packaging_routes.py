from flask import Blueprint, request, g
from backend.services.packaging_service import PackagingService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_packaging_data
from backend.utils.decorators import token_required, role_required

packaging_bp = Blueprint("packaging", __name__, url_prefix="/api/packaging")

@packaging_bp.route("", methods=["GET"])
@token_required
def get_packaging():
    order_id = request.args.get("orderId") or request.args.get("order_id")
    records = PackagingService.get_packaging(order_id=order_id)
    return list_response(data=records, count=len(records), message="Packaging records retrieved")

@packaging_bp.route("/<identifier>", methods=["GET"])
@token_required
def get_packaging_by_identifier(identifier):
    record = PackagingService.get_packaging_by_id(identifier)
    if record:
        return success_response(data=record, message="Packaging record retrieved")
    records = PackagingService.get_packaging(order_id=identifier)
    if records:
        return list_response(data=records, count=len(records), message=f"Packaging records for order {identifier}")
    return error_response("Packaging record not found", "NOT_FOUND", 404)

@packaging_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_packaging():
    data = request.get_json(silent=True) or {}
    errors = validate_packaging_data(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    pkg, message, err = PackagingService.create_packaging(data, user_id=user_id, user_name=user_name)
    if err:
        return error_response(message=message, error_code=err, status_code=400)

    return success_response(data=pkg, message=message, status_code=201)

@packaging_bp.route("/<packaging_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_packaging(packaging_id):
    data = request.get_json(silent=True) or {}
    updated, message, err = PackagingService.update_packaging(packaging_id, data)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)
