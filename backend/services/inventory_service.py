from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.models.inventory_model import InventoryModel

inventory_repo = FirestoreRepository("inventory")
transaction_repo = FirestoreRepository("inventoryTransactions")

class InventoryService:
    @staticmethod
    def _compute_status(quantity, minimum_stock):
        return InventoryModel.calculate_status(quantity, minimum_stock)

    @classmethod
    def create_material(cls, data, user_id=None, user_name=None):
        """Add new material/inventory item in Cloud Firestore."""
        mat_id = data.get("materialId")
        if mat_id:
            mat_id = str(mat_id).strip()
            existing = inventory_repo.get_by_id(mat_id)
            if existing:
                return None, f"Material with ID '{mat_id}' already exists"
        else:
            count = inventory_repo.count() + 1
            mat_id = f"MAT{count:03d}"

        quantity = float(data.get("quantity", 0))
        minimum_stock = float(data.get("minimumStock", 0))
        status = cls._compute_status(quantity, minimum_stock)

        item_record = {
            "materialId": mat_id,
            "id": mat_id,
            "materialName": data.get("materialName", "").strip(),
            "category": data.get("category", "Raw Materials").strip(),
            "quantity": quantity,
            "unit": data.get("unit", "units").strip(),
            "minimumStock": minimum_stock,
            "supplier": data.get("supplier", "").strip(),
            "status": status
        }
        created = inventory_repo.create(item_record, doc_id=mat_id)

        # Record initial transaction if quantity > 0
        if quantity > 0:
            txn_count = transaction_repo.count() + 1
            txn_id = f"TXN{txn_count:03d}"
            transaction_repo.create({
                "transactionId": txn_id,
                "id": txn_id,
                "materialId": mat_id,
                "type": "IN",
                "quantity": quantity,
                "reason": "Initial stock entry",
                "orderId": None,
                "createdBy": user_id or "SYSTEM"
            }, doc_id=txn_id)

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="INVENTORY_CREATED",
            entity_type="inventory",
            entity_id=mat_id,
            description=f"Created material {item_record['materialName']} ({quantity} {item_record['unit']})."
        )

        return created, None

    @staticmethod
    def get_inventory(category=None, status=None, search=None):
        """Retrieve inventory items with optional filters."""
        filters = {}
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status

        items = inventory_repo.get_all(filters=filters, sort_by="materialName")
        if search:
            items = [i for i in items if search.lower() in i.get("materialName", "").lower()]
        return items

    @staticmethod
    def get_material_by_id(material_id):
        """Retrieve single inventory item."""
        return inventory_repo.get_by_id(material_id)

    @classmethod
    def update_material(cls, material_id, update_data, user_id=None, user_name=None):
        """Update inventory metadata."""
        item = inventory_repo.get_by_id(material_id)
        if not item:
            return None, "Material not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["materialName", "category", "unit", "supplier"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        if "minimumStock" in update_data:
            safe_updates["minimumStock"] = float(update_data["minimumStock"])
            new_qty = float(safe_updates.get("quantity", item.get("quantity", 0)))
            safe_updates["status"] = cls._compute_status(new_qty, safe_updates["minimumStock"])

        updated = inventory_repo.update(material_id, safe_updates)

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="INVENTORY_UPDATED",
            entity_type="inventory",
            entity_id=material_id,
            description=f"Updated inventory details for {item.get('materialName')}."
        )

        return updated, "Material updated successfully", None

    @staticmethod
    def delete_material(material_id):
        """Delete inventory material."""
        item = inventory_repo.get_by_id(material_id)
        if not item:
            return False, "Material not found"
        return inventory_repo.delete(material_id), None

    @classmethod
    def stock_in(cls, material_id, quantity, reason, order_id=None, user_id=None, user_name=None):
        """Add stock to inventory and record transaction."""
        item = inventory_repo.get_by_id(material_id)
        if not item:
            return None, "Material not found", "NOT_FOUND"

        if quantity <= 0:
            return None, "Quantity must be greater than 0", "INVALID_QUANTITY"

        new_quantity = float(item.get("quantity", 0)) + float(quantity)
        new_status = cls._compute_status(new_quantity, item.get("minimumStock", 0))

        updated_item = inventory_repo.update(material_id, {
            "quantity": new_quantity,
            "status": new_status
        })

        txn_count = transaction_repo.count() + 1
        txn_id = f"TXN{txn_count:03d}"
        transaction_repo.create({
            "transactionId": txn_id,
            "id": txn_id,
            "materialId": material_id,
            "type": "IN",
            "quantity": float(quantity),
            "reason": reason,
            "orderId": order_id,
            "createdBy": user_id or "SYSTEM"
        }, doc_id=txn_id)

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="INVENTORY_UPDATED",
            entity_type="inventory",
            entity_id=material_id,
            description=f"Stock IN: +{quantity} {item.get('unit')} to {item.get('materialName')} (Reason: {reason})."
        )

        return updated_item, f"Stock increased by {quantity} {item.get('unit')}", None

    @classmethod
    def stock_out(cls, material_id, quantity, reason, order_id=None, user_id=None, user_name=None):
        """Reduce stock from inventory, prevent negative balance, and record transaction."""
        item = inventory_repo.get_by_id(material_id)
        if not item:
            return None, "Material not found", "NOT_FOUND"

        if quantity <= 0:
            return None, "Quantity must be greater than 0", "INVALID_QUANTITY"

        current_qty = float(item.get("quantity", 0))
        if quantity > current_qty:
            return None, f"Insufficient stock. Available: {current_qty} {item.get('unit')}, Requested: {quantity}", "INSUFFICIENT_STOCK"

        new_quantity = current_qty - float(quantity)
        new_status = cls._compute_status(new_quantity, item.get("minimumStock", 0))

        updated_item = inventory_repo.update(material_id, {
            "quantity": new_quantity,
            "status": new_status
        })

        txn_count = transaction_repo.count() + 1
        txn_id = f"TXN{txn_count:03d}"
        transaction_repo.create({
            "transactionId": txn_id,
            "id": txn_id,
            "materialId": material_id,
            "type": "OUT",
            "quantity": float(quantity),
            "reason": reason,
            "orderId": order_id,
            "createdBy": user_id or "SYSTEM"
        }, doc_id=txn_id)

        # Trigger notification if low stock or out of stock
        if new_status in ("Low Stock", "Out of Stock"):
            NotificationService.create_notification(
                user_id="ALL",
                notif_type="INVENTORY",
                title=f"{new_status} Alert",
                message=f"Material '{item.get('materialName')}' is now {new_status} (Remaining: {new_quantity} {item.get('unit')}).",
                order_id=order_id
            )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="INVENTORY_UPDATED",
            entity_type="inventory",
            entity_id=material_id,
            description=f"Stock OUT: -{quantity} {item.get('unit')} from {item.get('materialName')} (Reason: {reason})."
        )

        return updated_item, f"Stock reduced by {quantity} {item.get('unit')}", None

    @staticmethod
    def get_transactions(material_id=None):
        """Retrieve inventory transactions."""
        filters = {}
        if material_id:
            filters["materialId"] = material_id
        return transaction_repo.get_all(filters=filters, sort_by="createdAt", reverse=True)
