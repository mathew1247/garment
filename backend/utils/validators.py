import re
from backend.utils.helpers import is_valid_date

VALID_ORDER_PRIORITIES = {"Low", "Medium", "High", "Urgent"}
VALID_ORDER_STATUSES = {"Pending", "In Progress", "In Production", "Completed", "Cancelled", "Delayed", "Rework"}
VALID_PRODUCTION_STAGES = [
    "Cutting",
    "Stitching",
    "Finishing",
    "Quality Check",
    "Packaging",
    "Dispatch"
]
VALID_PRODUCTION_STATUSES = {"Pending", "In Progress", "Completed", "Failed", "Rework"}
VALID_INVENTORY_CATEGORIES = {"Raw Materials", "Work In Progress", "Finished Goods"}
VALID_ROLES = {"Administrator", "Manager", "Staff"}
VALID_QC_RESULTS = {"Pass", "Fail"}
VALID_TXN_TYPES = {"IN", "OUT", "ADJUSTMENT"}


def validate_order_data(data, is_update=False):
    """Validate order creation or update payload."""
    errors = []
    
    if not is_update or "customerName" in data:
        if not data.get("customerName") or not str(data.get("customerName")).strip():
            errors.append("Customer name is required and cannot be empty")
            
    if not is_update or ("productName" in data or "productType" in data):
        prod_title = data.get("productName") or data.get("productType")
        if not prod_title or not str(prod_title).strip():
            errors.append("Product name or type is required and cannot be empty")
            
    if not is_update or "quantity" in data:
        qty = data.get("quantity")
        if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
            errors.append("Quantity must be a positive number greater than 0")
            
    if not is_update or "deadline" in data:
        deadline = data.get("deadline")
        if not deadline or not is_valid_date(str(deadline)):
            errors.append("Valid deadline in YYYY-MM-DD format is required")
            
    if "priority" in data and data.get("priority"):
        if data.get("priority") not in VALID_ORDER_PRIORITIES:
            errors.append(f"Priority must be one of: {', '.join(sorted(VALID_ORDER_PRIORITIES))}")
            
    if "status" in data and data.get("status"):
        if data.get("status") not in VALID_ORDER_STATUSES:
            errors.append(f"Status must be one of: {', '.join(sorted(VALID_ORDER_STATUSES))}")
            
    return errors


def validate_employee_data(data, is_update=False):
    """Validate employee payload."""
    errors = []
    
    if not is_update or "name" in data:
        if not data.get("name") or not str(data.get("name")).strip():
            errors.append("Employee name is required")
            
    if not is_update or "department" in data:
        if not data.get("department") or not str(data.get("department")).strip():
            errors.append("Department is required")
            
    if not is_update or "role" in data:
        if not data.get("role") or not str(data.get("role")).strip():
            errors.append("Role is required")
            
    if not is_update or "phone" in data:
        if not data.get("phone") or not str(data.get("phone")).strip():
            errors.append("Phone number is required")
            
    if not is_update or "email" in data:
        email = str(data.get("email", "")).strip()
        if not email or "@" not in email:
            errors.append("Valid email is required")
            
    return errors


def validate_inventory_data(data, is_update=False):
    """Validate inventory item data."""
    errors = []
    
    if not is_update or "materialName" in data:
        if not data.get("materialName") or not str(data.get("materialName")).strip():
            errors.append("Material name is required")
            
    if not is_update or "category" in data:
        cat = data.get("category")
        if not cat or cat not in VALID_INVENTORY_CATEGORIES:
            errors.append(f"Category must be one of: {', '.join(sorted(VALID_INVENTORY_CATEGORIES))}")
            
    if not is_update or "quantity" in data:
        qty = data.get("quantity")
        if qty is None or not isinstance(qty, (int, float)) or qty < 0:
            errors.append("Quantity must be a non-negative number")
            
    if not is_update or "minimumStock" in data:
        min_stock = data.get("minimumStock")
        if min_stock is None or not isinstance(min_stock, (int, float)) or min_stock < 0:
            errors.append("Minimum stock must be a non-negative number")
            
    if not is_update or "unit" in data:
        if not data.get("unit") or not str(data.get("unit")).strip():
            errors.append("Unit (e.g. meters, spools, pieces) is required")
            
    return errors


def validate_stock_transaction(data):
    """Validate stock IN/OUT transaction."""
    errors = []
    qty = data.get("quantity")
    if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
        errors.append("Transaction quantity must be greater than 0")
        
    reason = data.get("reason")
    if not reason or not str(reason).strip():
        errors.append("Reason for transaction is required")
        
    return errors


def validate_quality_check(data):
    """Validate quality check payload."""
    errors = []
    if not data.get("orderId"):
        errors.append("Order ID is required")
    result = data.get("result")
    if not result or result not in VALID_QC_RESULTS:
        errors.append("Result must be either 'Pass' or 'Fail'")
        
    defect_qty = data.get("defectQuantity", 0)
    if defect_qty is not None and (not isinstance(defect_qty, (int, float)) or defect_qty < 0):
        errors.append("Defect quantity cannot be negative")
        
    return errors


def validate_assignment_data(data):
    """Validate worker assignment data."""
    errors = []
    if not data.get("employeeId"):
        errors.append("Employee ID is required")
    if not data.get("orderId"):
        errors.append("Order ID is required")
    if not data.get("productionId"):
        errors.append("Production ID is required")
    if not data.get("stage") or data.get("stage") not in VALID_PRODUCTION_STAGES:
        errors.append(f"Stage must be one of: {', '.join(VALID_PRODUCTION_STAGES)}")
        
    qty = data.get("quantity")
    if qty is not None and (not isinstance(qty, (int, float)) or qty <= 0):
        errors.append("Assigned quantity must be greater than 0")
        
    return errors


def validate_packaging_data(data):
    """Validate packaging payload."""
    errors = []
    if not data.get("orderId"):
        errors.append("Order ID is required")
    qty = data.get("quantity")
    if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
        errors.append("Packaged quantity must be greater than 0")
    return errors


def validate_dispatch_data(data):
    """Validate dispatch payload."""
    errors = []
    if not data.get("orderId"):
        errors.append("Order ID is required")
    if not data.get("deliveryInformation") or not str(data.get("deliveryInformation")).strip():
        errors.append("Delivery information is required")
    return errors
