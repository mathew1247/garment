from flask import Blueprint, request, g
from backend.services.inventory_service import InventoryService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.validators import validate_inventory_data, validate_stock_transaction
from backend.utils.decorators import token_required, role_required

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")

@inventory_bp.route("", methods=["GET"])
@token_required
def get_inventory():
    category = request.args.get("category")
    status = request.args.get("status")
    search = request.args.get("search")

    items = InventoryService.get_inventory(category=category, status=status, search=search)
    return list_response(data=items, count=len(items), message="Inventory items retrieved")

@inventory_bp.route("/<material_id>", methods=["GET"])
@token_required
def get_material(material_id):
    item = InventoryService.get_material_by_id(material_id)
    if not item:
        return error_response("Material not found", "NOT_FOUND", 404)
    return success_response(data=item, message="Material retrieved")

@inventory_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_material():
    data = request.get_json(silent=True) or {}
    errors = validate_inventory_data(data, is_update=False)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")
    data["createdBy"] = user_id or "SYSTEM"
    created, err = InventoryService.create_material(data, user_id=user_id, user_name=user_name)
    if err:
        return error_response(err, "DUPLICATE_MATERIAL", 409)
    return success_response(data=created, message="Material added to inventory", status_code=201)

@inventory_bp.route("/<material_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_material(material_id):
    data = request.get_json(silent=True) or {}
    errors = validate_inventory_data(data, is_update=True)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")
    updated, message, err = InventoryService.update_material(material_id, data, user_id=user_id, user_name=user_name)
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)
    return success_response(data=updated, message=message)

@inventory_bp.route("/<material_id>", methods=["DELETE"])
@token_required
@role_required("Administrator")
def delete_material(material_id):
    success, err = InventoryService.delete_material(material_id)
    if not success:
        return error_response(err or "Material not found", "NOT_FOUND", 404)
    return success_response(message="Material deleted successfully")

@inventory_bp.route("/<material_id>/stock-in", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def stock_in(material_id):
    data = request.get_json(silent=True) or {}
    errors = validate_stock_transaction(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    quantity = float(data.get("quantity"))
    reason = data.get("reason")
    order_id = data.get("orderId")
    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    updated, message, err = InventoryService.stock_in(
        material_id=material_id,
        quantity=quantity,
        reason=reason,
        order_id=order_id,
        user_id=user_id,
        user_name=user_name
    )
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)

    return success_response(data=updated, message=message)

@inventory_bp.route("/<material_id>/stock-out", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def stock_out(material_id):
    data = request.get_json(silent=True) or {}
    errors = validate_stock_transaction(data)
    if errors:
        return error_response(message=errors[0], error_code="VALIDATION_ERROR", status_code=400, details=errors)

    quantity = float(data.get("quantity"))
    reason = data.get("reason")
    order_id = data.get("orderId")
    user = getattr(g, "current_user", {})
    user_id = user.get("uid") or user.get("id")
    user_name = user.get("name")

    updated, message, err = InventoryService.stock_out(
        material_id=material_id,
        quantity=quantity,
        reason=reason,
        order_id=order_id,
        user_id=user_id,
        user_name=user_name
    )
    if err:
        return error_response(message, err, 404 if err == "NOT_FOUND" else 400)

    return success_response(data=updated, message=message)

@inventory_bp.route("/<material_id>/transactions", methods=["GET"])
@token_required
def get_transactions(material_id):
    txns = InventoryService.get_transactions(material_id=material_id)
    return list_response(data=txns, count=len(txns), message="Transactions retrieved")
