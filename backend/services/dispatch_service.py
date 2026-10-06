from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp

dispatch_repo = FirestoreRepository("dispatch")
packaging_repo = FirestoreRepository("packaging")
production_repo = FirestoreRepository("production")
order_repo = FirestoreRepository("orders")

class DispatchService:
    @staticmethod
    def create_dispatch(data, user_id=None, user_name=None):
        """
        Record dispatch for an order in Cloud Firestore:
        - Rule: Dispatch ONLY after packaging is completed.
        - Production Dispatch stage -> Completed.
        - Order status -> Completed.
        - Order currentStage -> Completed.
        - Send notification & audit log.
        """
        order_id = data.get("orderId")
        order = order_repo.get_by_id(order_id)
        if not order:
            return None, "Order not found", "ORDER_NOT_FOUND"

        # Check packaging completed
        pkg_records = packaging_repo.get_all(filters={"orderId": order_id, "status": "Completed"})
        stages = production_repo.get_all(filters={"orderId": order_id})
        pkg_stage = next((s for s in stages if s["stage"] == "Packaging"), None)

        is_packaging_done = len(pkg_records) > 0 or (pkg_stage and pkg_stage.get("status") == "Completed")
        if not is_packaging_done:
            return None, "Dispatch cannot be processed before Packaging is completed.", "PACKAGING_NOT_COMPLETED"

        now = get_current_timestamp()
        dsp_id = data.get("dispatchId")
        if dsp_id:
            dsp_id = str(dsp_id).strip()
            existing = dispatch_repo.get_by_id(dsp_id)
            if existing:
                return None, f"Dispatch record '{dsp_id}' already exists", "DUPLICATE_DISPATCH"
        else:
            dsp_count = dispatch_repo.count() + 1
            dsp_id = f"DSP{dsp_count:03d}"

        dispatch_record = {
            "dispatchId": dsp_id,
            "id": dsp_id,
            "orderId": order_id,
            "dispatchDate": data.get("dispatchDate") or now,
            "deliveryInformation": data.get("deliveryInformation", "").strip(),
            "status": data.get("status", "Dispatched"),
            "remarks": data.get("remarks", "")
        }

        created_dsp = dispatch_repo.create(dispatch_record, doc_id=dsp_id)

        # Update production stage Dispatch -> Completed
        dsp_stage = next((s for s in stages if s["stage"] == "Dispatch"), None)
        if dsp_stage:
            production_repo.update(dsp_stage["productionId"], {
                "status": "Completed",
                "progress": 100,
                "completedQuantity": dsp_stage.get("quantity", order.get("quantity", 0)),
                "completedDate": now,
                "remarks": f"Dispatched: {dispatch_record['deliveryInformation']}"
            })

        # Update order status to Completed and currentStage to Completed
        order_repo.update(order_id, {
            "status": "Completed",
            "currentStage": "Completed"
        })

        NotificationService.create_notification(
            user_id="ALL",
            notif_type="DISPATCH",
            title="Order Dispatched",
            message=f"Order {order_id} has been dispatched to {dispatch_record['deliveryInformation']}. Order marked as Completed.",
            order_id=order_id
        )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="DISPATCH_COMPLETED",
            entity_type="dispatch",
            entity_id=dsp_id,
            description=f"Order {order_id} dispatched to {dispatch_record['deliveryInformation']}. Order completed."
        )

        return created_dsp, "Order successfully dispatched and marked as Completed", None

    @staticmethod
    def get_dispatches(order_id=None):
        """Retrieve dispatches."""
        filters = {}
        if order_id:
            filters["orderId"] = order_id
        return dispatch_repo.get_all(filters=filters, sort_by="dispatchDate", reverse=True)

    @staticmethod
    def get_dispatch_by_id(dispatch_id):
        """Retrieve single dispatch record."""
        return dispatch_repo.get_by_id(dispatch_id)

    @staticmethod
    def update_dispatch(dispatch_id, update_data):
        """Update dispatch record."""
        dsp = dispatch_repo.get_by_id(dispatch_id)
        if not dsp:
            return None, "Dispatch record not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["deliveryInformation", "status", "dispatchDate", "remarks"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        updated = dispatch_repo.update(dispatch_id, safe_updates)
        return updated, "Dispatch record updated", None
