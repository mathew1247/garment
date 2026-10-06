from flask import Blueprint, request, g
from backend.services.assignment_service import AssignmentService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_assignment_data
from backend.utils.decorators import token_required, role_required

assignment_bp = Blueprint("assignments", __name__, url_prefix="/api/assignments")

@assignment_bp.route("", methods=["GET"])
@token_required
def get_assignments():
    emp_id = request.args.get("employeeId") or request.args.get("employee_id")
    order_id = request.args.get("orderId") or request.args.get("order_id")
    status = request.args.get("status")

    assignments = AssignmentService.get_assignments(
        employee_id=emp_id,
        order_id=order_id,
        status=status
    )
    return list_response(data=assignments, count=len(assignments), message="Assignments retrieved")

@assignment_bp.route("/<assignment_id>", methods=["GET"])
@token_required
def get_assignment(assignment_id):
    asn = AssignmentService.get_assignment_by_id(assignment_id)
    if not asn:
        return error_response("Assignment not found", "NOT_FOUND", 404)
    return success_response(data=asn, message="Assignment retrieved")

@assignment_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_assignment():
    data = request.get_json(silent=True) or {}
    errors = validate_assignment_data(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    asn, message, err = AssignmentService.create_assignment(data, user_id=user_id, user_name=user_name)
    if err:
        return error_response(message=message, error_code=err, status_code=400)

    return success_response(data=asn, message=message, status_code=201)

@assignment_bp.route("/<assignment_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_assignment(assignment_id):
    data = request.get_json(silent=True) or {}
    updated, message, err = AssignmentService.update_assignment(assignment_id, data)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)

@assignment_bp.route("/<assignment_id>", methods=["DELETE"])
@token_required
@role_required("Administrator", "Manager")
def delete_assignment(assignment_id):
    success = AssignmentService.delete_assignment(assignment_id)
    if not success:
        return error_response("Assignment not found", "NOT_FOUND", 404)
    return success_response(message="Assignment deleted successfully")
