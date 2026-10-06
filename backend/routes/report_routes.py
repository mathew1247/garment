from flask import Blueprint, request
from backend.services.report_service import ReportService
from backend.utils.responses import success_response
from backend.utils.decorators import token_required, role_required

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@report_bp.route("/production", methods=["GET"])
@token_required
@role_required("Administrator", "Manager")
def get_production_report():
    stage = request.args.get("stage")
    status = request.args.get("status")
    employee_id = request.args.get("employeeId") or request.args.get("employee_id")

    report = ReportService.get_production_report(stage=stage, status=status, employee_id=employee_id)
    return success_response(data=report, message="Production report generated successfully")

@report_bp.route("/orders", methods=["GET"])
@token_required
@role_required("Administrator", "Manager")
def get_order_report():
    status = request.args.get("status")
    priority = request.args.get("priority")

    report = ReportService.get_order_report(status=status, priority=priority)
    return success_response(data=report, message="Order report generated successfully")

@report_bp.route("/employees", methods=["GET"])
@token_required
@role_required("Administrator", "Manager")
def get_employee_report():
    department = request.args.get("department")

    report = ReportService.get_employee_report(department=department)
    return success_response(data=report, message="Employee performance report generated successfully")

@report_bp.route("/inventory", methods=["GET"])
@token_required
@role_required("Administrator", "Manager")
def get_inventory_report():
    category = request.args.get("category")

    report = ReportService.get_inventory_report(category=category)
    return success_response(data=report, message="Inventory report generated successfully")
