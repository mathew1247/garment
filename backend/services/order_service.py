from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import is_past_date, get_current_timestamp
from backend.utils.validators import VALID_PRODUCTION_STAGES

order_repo = FirestoreRepository("orders")
production_repo = FirestoreRepository("production")

class OrderService:
    @staticmethod
    def create_order(data, created_by=None, user_name=None):
        """
        Create a new order in Cloud Firestore:
        1. Generate unique orderId
        2. Save order document
        3. Create 6 sequential production stages in 'production' collection
        4. Set Cutting as first active stage
        5. Create notification
        6. Create audit log
        """
        order_id = data.get("orderId")
        if order_id:
            order_id = str(order_id).strip()
            existing = order_repo.get_by_id(order_id)
            if existing:
                return None, f"Order with ID '{order_id}' already exists", "DUPLICATE_ORDER"
        else:
            count = order_repo.count() + 1
            order_id = f"ORD{count:03d}"

        order_record = {
            "orderId": order_id,
            "id": order_id,
            "customerName": data.get("customerName", "").strip(),
            "customerContact": data.get("customerContact", "").strip(),
            "productId": data.get("productId", ""),
            "productName": (data.get("productName") or data.get("productType") or "").strip(),
            "productType": data.get("productType", "General").strip(),
            "quantity": int(data.get("quantity", 0)),
            "deadline": data.get("deadline"),
            "specifications": data.get("specifications", ""),
            "fabricType": data.get("fabricType", ""),
            "color": data.get("color", ""),
            "sizes": data.get("sizes", []),
            "priority": data.get("priority", "Medium"),
            "status": data.get("status", "In Production"),
            "currentStage": "Cutting",
            "createdBy": created_by or "SYSTEM"
        }

        created_order = order_repo.create(order_record, doc_id=order_id)

        # Automatically create 6 sequential production stages in Firestore
        for idx, stage_name in enumerate(VALID_PRODUCTION_STAGES, 1):
            stage_status = "In Progress" if idx == 1 else "Pending"
            start_date = get_current_timestamp() if idx == 1 else None
            prod_id = f"{order_id}_{idx}"

            stage_record = {
                "productionId": prod_id,
                "id": prod_id,
                "orderId": order_id,
                "stage": stage_name,
                "status": stage_status,
                "assignedEmployeeId": None,
                "assignedEmployeeName": None,
                "quantity": int(created_order["quantity"]),
                "completedQuantity": 0,
                "progress": 0,
                "startDate": start_date,
                "expectedCompletion": created_order["deadline"],
                "completedDate": None,
                "remarks": "Initialized stage" if idx == 1 else ""
            }
            production_repo.create(stage_record, doc_id=prod_id)

        # Create system notification
        NotificationService.create_notification(
            user_id="ALL",
            notif_type="ORDER",
            title="New Order Created",
            message=f"Order {order_id} ({created_order['productName']}) for {created_order['customerName']} has been created.",
            order_id=order_id
        )

        # Create audit log
        AuditService.log(
            user_id=created_by,
            user_name=user_name,
            action="ORDER_CREATED",
            entity_type="orders",
            entity_id=order_id,
            description=f"Created order {order_id} for {created_order['customerName']} ({created_order['quantity']} units)."
        )

        return created_order, None, None

    @staticmethod
    def get_orders(status=None, priority=None, customer=None):
        """Retrieve orders with Firestore queries and dynamic delayed checking."""
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority

        orders = order_repo.get_all(filters=filters, sort_by="createdAt", reverse=True)

        results = []
        for ord_item in orders:
            # Check customer filter
            if customer and customer.lower() not in ord_item.get("customerName", "").lower():
                continue

            # Auto-detect delayed if past deadline
            if ord_item.get("status") not in ("Completed", "Cancelled") and is_past_date(ord_item.get("deadline")):
                if ord_item.get("status") != "Delayed":
                    ord_item["status"] = "Delayed"
                    order_repo.update(ord_item["orderId"], {"status": "Delayed"})

            results.append(ord_item)

        return results

    @staticmethod
    def get_order_by_id(order_id):
        """Get single order along with all production stages from Firestore."""
        order = order_repo.get_by_id(order_id)
        if not order:
            return None

        stages = production_repo.get_all(filters={"orderId": order_id}, sort_by="productionId")
        order_copy = dict(order)
        order_copy["stages"] = stages
        return order_copy

    @staticmethod
    def update_order(order_id, update_data, user_id=None, user_name=None):
        """Update order details and record audit log."""
        order = order_repo.get_by_id(order_id)
        if not order:
            return None

        safe_updates = {}
        allowed_fields = [
            "customerName", "customerContact", "productId", "productName", "productType",
            "quantity", "deadline", "specifications", "fabricType", "color",
            "sizes", "priority", "status", "currentStage"
        ]
        for field in allowed_fields:
            if field in update_data:
                safe_updates[field] = update_data[field]

        updated = order_repo.update(order_id, safe_updates)

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="ORDER_UPDATED",
            entity_type="orders",
            entity_id=order_id,
            description=f"Updated order {order_id} fields: {', '.join(safe_updates.keys())}"
        )

        return updated

    @staticmethod
    def delete_order(order_id, user_id=None, user_name=None):
        """Delete an order and its associated production records from Firestore."""
        order = order_repo.get_by_id(order_id)
        if not order:
            return False

        stages = production_repo.get_all(filters={"orderId": order_id})
        for s in stages:
            production_repo.delete(s["productionId"])

        deleted = order_repo.delete(order_id)
        if deleted:
            AuditService.log(
                user_id=user_id,
                user_name=user_name,
                action="ORDER_DELETED",
                entity_type="orders",
                entity_id=order_id,
                description=f"Deleted order {order_id} and all associated production stages."
            )
        return deleted
