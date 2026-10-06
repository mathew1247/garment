from flask import Blueprint, request
from backend.services.employee_service import EmployeeService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_employee_data
from backend.utils.decorators import token_required, role_required

employee_bp = Blueprint("employees", __name__, url_prefix="/api/employees")

@employee_bp.route("", methods=["GET"])
@token_required
def get_employees():
    department = request.args.get("department")
    role = request.args.get("role")
    status = request.args.get("status")

    employees = EmployeeService.get_employees(department=department, role=role, status=status)
    return list_response(data=employees, count=len(employees), message="Employees retrieved successfully")

@employee_bp.route("/<employee_id>", methods=["GET"])
@token_required
def get_employee(employee_id):
    emp = EmployeeService.get_employee_by_id(employee_id)
    if not emp:
        return error_response("Employee not found", "NOT_FOUND", 404)
    return success_response(data=emp, message="Employee retrieved successfully")

@employee_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_employee():
    data = request.get_json(silent=True) or {}
    errors = validate_employee_data(data, is_update=False)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    emp, err = EmployeeService.create_employee(data)
    if err:
        return error_response(err, "DUPLICATE_EMPLOYEE", 409)
    return success_response(data=emp, message="Employee created successfully", status_code=201)

@employee_bp.route("/<employee_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}
    errors = validate_employee_data(data, is_update=True)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    emp, message, err = EmployeeService.update_employee(employee_id, data)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=emp, message=message)

@employee_bp.route("/<employee_id>", methods=["DELETE"])
@token_required
@role_required("Administrator")
def delete_employee(employee_id):
    success, err = EmployeeService.delete_employee(employee_id)
    if not success:
        return error_response(err or "Employee not found", "DELETE_FAILED", 404)
    return success_response(message="Employee deleted successfully")

@employee_bp.route("/<employee_id>/performance", methods=["GET"])
@token_required
def get_employee_performance(employee_id):
    perf, message, err = EmployeeService.get_employee_performance(employee_id)
    if err:
        return error_response(message, err, 404)
    return success_response(data=perf, message=message)
