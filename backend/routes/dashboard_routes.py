from flask import Blueprint
from backend.services.dashboard_service import DashboardService
from backend.utils.responses import success_response
from backend.utils.decorators import token_required, role_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("", methods=["GET"])
@token_required
@role_required("Administrator", "Manager")
def get_dashboard():
    stats = DashboardService.get_dashboard_data()
    return success_response(data=stats, message="Dashboard statistics retrieved successfully")
