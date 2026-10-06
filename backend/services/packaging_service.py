from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp

packaging_repo = FirestoreRepository("packaging")
quality_repo = FirestoreRepository("qualityChecks")
production_repo = FirestoreRepository("production")
order_repo = FirestoreRepository("orders")

class PackagingService:
    @staticmethod
    def create_packaging(data, user_id=None, user_name=None):
        """
        Record packaging for an order in Cloud Firestore:
        - Strict Rule: Packaging can start ONLY after Quality Check = Pass.
        - Marks Packaging production stage as Completed.
        - Sets Dispatch production stage to In Progress.
        - Updates Order currentStage to Dispatch.
        - Sends notification & audit log.
        """
        order_id = data.get("orderId")
        order = order_repo.get_by_id(order_id)
        if not order:
            return None, "Order not found", "ORDER_NOT_FOUND"

        # Check QC Pass requirement in Firestore
        qc_records = quality_repo.get_all(filters={"orderId": order_id, "result": "Pass"})
        stages = production_repo.get_all(filters={"orderId": order_id})
        qc_stage = next((s for s in stages if s["stage"] == "Quality Check"), None)

        is_qc_passed = len(qc_records) > 0 or (qc_stage and qc_stage.get("status") == "Completed")
        if not is_qc_passed:
            return None, "Packaging cannot start until Quality Check is Passed.", "QC_NOT_PASSED"

        now = get_current_timestamp()
        pkg_id = data.get("packagingId")
        if pkg_id:
            pkg_id = str(pkg_id).strip()
            existing = packaging_repo.get_by_id(pkg_id)
            if existing:
                return None, f"Packaging record '{pkg_id}' already exists", "DUPLICATE_PACKAGING"
        else:
            pkg_count = packaging_repo.count() + 1
            pkg_id = f"PKG{pkg_count:03d}"

        pkg_record = {
            "packagingId": pkg_id,
            "id": pkg_id,
            "orderId": order_id,
            "quantity": int(data.get("quantity", order.get("quantity", 0))),
            "status": data.get("status", "Completed"),
            "packedDate": data.get("packedDate") or now,
            "remarks": data.get("remarks", "")
        }

        created_pkg = packaging_repo.create(pkg_record, doc_id=pkg_id)

        # Update production stage Packaging -> Completed
        pkg_stage = next((s for s in stages if s["stage"] == "Packaging"), None)
        if pkg_stage:
            production_repo.update(pkg_stage["productionId"], {
                "status": "Completed",
                "progress": 100,
                "completedQuantity": pkg_record["quantity"],
                "completedDate": now,
                "remarks": pkg_record["remarks"]
            })

        # Advance Dispatch stage to In Progress
        dispatch_stage = next((s for s in stages if s["stage"] == "Dispatch"), None)
        if dispatch_stage:
            production_repo.update(dispatch_stage["productionId"], {
                "status": "In Progress",
                "startDate": now
            })

        # Update order currentStage
        order_repo.update(order_id, {
            "currentStage": "Dispatch"
        })

        NotificationService.create_notification(
            user_id="ALL",
            notif_type="PACKAGING",
            title="Packaging Completed",
            message=f"Order {order_id} packaging completed ({pkg_record['quantity']} units). Ready for Dispatch.",
            order_id=order_id
        )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="PACKAGING_COMPLETED",
            entity_type="packaging",
            entity_id=pkg_id,
            description=f"Packaging completed for Order {order_id} ({pkg_record['quantity']} units)."
        )

        return created_pkg, "Packaging recorded successfully", None

    @staticmethod
    def get_packaging(order_id=None):
        """Get packaging records."""
        filters = {}
        if order_id:
            filters["orderId"] = order_id
        return packaging_repo.get_all(filters=filters, sort_by="packedDate", reverse=True)

    @staticmethod
    def get_packaging_by_id(pkg_id):
        """Get single packaging record."""
        return packaging_repo.get_by_id(pkg_id)

    @staticmethod
    def update_packaging(pkg_id, update_data):
        """Update packaging record."""
        pkg = packaging_repo.get_by_id(pkg_id)
        if not pkg:
            return None, "Packaging record not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["quantity", "status", "packedDate", "remarks"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        updated = packaging_repo.update(pkg_id, safe_updates)
        return updated, "Packaging updated successfully", None
