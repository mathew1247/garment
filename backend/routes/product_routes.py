from flask import Blueprint, request
from backend.services.product_service import ProductService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.decorators import token_required, role_required

product_bp = Blueprint("products", __name__, url_prefix="/api/products")

@product_bp.route("", methods=["GET"])
@token_required
def get_products():
    products = ProductService.get_products()
    return list_response(data=products, count=len(products), message="Products retrieved successfully")

@product_bp.route("/<product_id>", methods=["GET"])
@token_required
def get_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    if not product:
        return error_response("Product not found", "NOT_FOUND", 404)
    return success_response(data=product, message="Product retrieved successfully")

@product_bp.route("", methods=["POST"])
@token_required
@role_required("Administrator", "Manager")
def create_product():
    data = request.get_json(silent=True) or {}
    if not data.get("productName"):
        return error_response("Product name is required", "VALIDATION_ERROR", 400)
    created, err = ProductService.create_product(data)
    if err:
        return error_response(err, "DUPLICATE_PRODUCT", 409)
    return success_response(data=created, message="Product created successfully", status_code=201)

@product_bp.route("/<product_id>", methods=["PUT"])
@token_required
@role_required("Administrator", "Manager")
def update_product(product_id):
    data = request.get_json(silent=True) or {}
    updated, err = ProductService.update_product(product_id, data)
    if err:
        return error_response(err, "UPDATE_FAILED", 404)
    return success_response(data=updated, message="Product updated successfully")

@product_bp.route("/<product_id>", methods=["DELETE"])
@token_required
@role_required("Administrator")
def delete_product(product_id):
    success = ProductService.delete_product(product_id)
    if not success:
        return error_response("Product not found", "NOT_FOUND", 404)
    return success_response(message="Product deleted successfully")
