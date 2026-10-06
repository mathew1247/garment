from flask import Blueprint, request, g
from backend.services.quality_service import QualityService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_quality_check
from backend.utils.decorators import token_required, role_required

quality_bp = Blueprint("quality", __name__, url_prefix="/api/quality-checks")

@quality_bp.route("", methods=["GET"])
@token_required
def get_quality_checks():
    order_id = request.args.get("orderId") or request.args.get("order_id")
    records = QualityService.get_quality_checks(order_id=order_id)
    return list_response(data=records, count=len(records), message="Quality checks retrieved")

@quality_bp.route("/<identifier>", methods=["GET"])
@token_required
def get_quality_check_by_identifier(identifier):
    record = QualityService.get_quality_check_by_id(identifier)
    if record:
        return success_response(data=record, message="Quality check retrieved")
    records = QualityService.get_quality_checks(order_id=identifier)
    if records:
        return list_response(data=records, count=len(records), message=f"Quality checks for order {identifier}")
    return error_response("Quality check record not found", "NOT_FOUND", 404)

@quality_bp.route("", methods=["POST"])
@token_required
def create_quality_check():
    data = request.get_json(silent=True) or {}
    errors = validate_quality_check(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")
    inspector_id = data.get("inspectorId") or user_id

    qc, message, err = QualityService.create_quality_check(
        data=data,
        inspector_id=inspector_id,
        user_id=user_id,
        user_name=user_name
    )
    if err:
        return error_response(message=message, error_code=err, status_code=400)

    return success_response(data=qc, message=message, status_code=201)

@quality_bp.route("/<quality_check_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_quality_check(quality_check_id):
    data = request.get_json(silent=True) or {}
    updated, message, err = QualityService.update_quality_check(quality_check_id, data)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)
