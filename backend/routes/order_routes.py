from flask import Blueprint, request, g
from backend.services.order_service import OrderService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_order_data
from backend.utils.decorators import token_required, role_required

order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

@order_bp.route("", methods=["GET"])
@token_required
def get_orders():
    status = request.args.get("status")
    priority = request.args.get("priority")
    customer = request.args.get("customer")

    orders = OrderService.get_orders(status=status, priority=priority, customer=customer)
    return list_response(data=orders, count=len(orders), message="Orders retrieved successfully")

@order_bp.route("/<order_id>", methods=["GET"])
@token_required
def get_order(order_id):
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return error_response(message="Order not found", error_code="ORDER_NOT_FOUND", status_code=404)
    return success_response(data=order, message="Order retrieved successfully")

@order_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_order():
    data = request.get_json(silent=True) or {}
    errors = validate_order_data(data, is_update=False)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    created_by = user.get("uid") or user.get("id") or "USR001"
    user_name = user.get("name", "User")
    order, err_msg, err_code = OrderService.create_order(data, created_by=created_by, user_name=user_name)
    if err_msg:
        status_code = 409 if err_code == "DUPLICATE_ORDER" else 400
        return error_response(message=err_msg, error_code=err_code or "ORDER_CREATION_FAILED", status_code=status_code)
    return success_response(data=order, message="Order created successfully", status_code=201)

@order_bp.route("/<order_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_order(order_id):
    data = request.get_json(silent=True) or {}
    errors = validate_order_data(data, is_update=True)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")
    updated = OrderService.update_order(order_id, data, user_id=user_id, user_name=user_name)
    if not updated:
        return error_response(message="Order not found", error_code="ORDER_NOT_FOUND", status_code=404)
    return success_response(data=updated, message="Order updated successfully")

@order_bp.route("/<order_id>", methods=["DELETE"])
@token_required
@role_required("Administrator")
def delete_order(order_id):
    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")
    success = OrderService.delete_order(order_id, user_id=user_id, user_name=user_name)
    if not success:
        return error_response(message="Order not found", error_code="ORDER_NOT_FOUND", status_code=404)
    return success_response(message="Order deleted successfully")
