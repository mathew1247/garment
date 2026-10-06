from flask import Blueprint, request, g
from backend.services.dispatch_service import DispatchService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_dispatch_data
from backend.utils.decorators import token_required, role_required

dispatch_bp = Blueprint("dispatch", __name__, url_prefix="/api/dispatch")

@dispatch_bp.route("", methods=["GET"])
@token_required
def get_dispatches():
    order_id = request.args.get("orderId") or request.args.get("order_id")
    records = DispatchService.get_dispatches(order_id=order_id)
    return list_response(data=records, count=len(records), message="Dispatch records retrieved")

@dispatch_bp.route("/<identifier>", methods=["GET"])
@token_required
def get_dispatch_by_identifier(identifier):
    record = DispatchService.get_dispatch_by_id(identifier)
    if record:
        return success_response(data=record, message="Dispatch record retrieved")
    records = DispatchService.get_dispatches(order_id=identifier)
    if records:
        return list_response(data=records, count=len(records), message=f"Dispatch records for order {identifier}")
    return error_response("Dispatch record not found", "NOT_FOUND", 404)

@dispatch_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_dispatch():
    data = request.get_json(silent=True) or {}
    errors = validate_dispatch_data(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    dsp, message, err = DispatchService.create_dispatch(data, user_id=user_id, user_name=user_name)
    if err:
        return error_response(message=message, error_code=err, status_code=400)

    return success_response(data=dsp, message=message, status_code=201)

@dispatch_bp.route("/<dispatch_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_dispatch(dispatch_id):
    data = request.get_json(silent=True) or {}
    updated, message, err = DispatchService.update_dispatch(dispatch_id, data)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)
