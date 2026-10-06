from flask import Blueprint, request, g
from backend.services.production_service import ProductionService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.decorators import token_required

production_bp = Blueprint("production", __name__, url_prefix="/api/production")

@production_bp.route("", methods=["GET"])
@token_required
def get_production():
    order_id = request.args.get("orderId") or request.args.get("order_id")
    stage = request.args.get("stage")
    status = request.args.get("status")
    employee_id = request.args.get("employeeId") or request.args.get("employee_id")

    records = ProductionService.get_production_records(
        order_id=order_id,
        stage=stage,
        status=status,
        employee_id=employee_id
    )
    return list_response(data=records, count=len(records), message="Production records retrieved")

@production_bp.route("/<identifier>", methods=["GET"])
@token_required
def get_production_by_identifier(identifier):
    if identifier.startswith("PROD") or "_" in identifier:
        record = ProductionService.get_production_by_id(identifier)
        if not record:
            return error_response("Production record not found", "NOT_FOUND", 404)
        return success_response(data=record, message="Production record retrieved")
    else:
        records = ProductionService.get_production_records(order_id=identifier)
        return list_response(data=records, count=len(records), message=f"Production stages for order {identifier}")

@production_bp.route("/<production_id>", methods=["PUT"])
@token_required
def update_production(production_id):
    data = request.get_json(silent=True) or {}
    updated, message, err = ProductionService.update_production(production_id, data)
    if err:
        return error_response(message=message, error_code=err, status_code=404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)

@production_bp.route("/<production_id>/start", methods=["POST"])
@token_required
def start_stage(production_id):
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employeeId")
    remarks = data.get("remarks")

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    updated, message, err = ProductionService.start_stage(
        production_id=production_id,
        employee_id=employee_id,
        remarks=remarks,
        user_id=user_id,
        user_name=user_name
    )
    if err:
        status_code = 404 if err == "NOT_FOUND" else 400
        return error_response(message=message, error_code=err, status_code=status_code)

    return success_response(data=updated, message=message)

@production_bp.route("/<production_id>/complete", methods=["POST"])
@token_required
def complete_stage(production_id):
    data = request.get_json(silent=True) or {}
    completed_qty = data.get("completedQuantity")
    remarks = data.get("remarks")

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    updated, message, err = ProductionService.complete_stage(
        production_id=production_id,
        completed_quantity=completed_qty,
        remarks=remarks,
        user_id=user_id,
        user_name=user_name
    )
    if err:
        status_code = 404 if err == "NOT_FOUND" else 400
        return error_response(message=message, error_code=err, status_code=status_code)

    return success_response(data=updated, message=message)
