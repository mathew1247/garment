from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp

quality_repo = FirestoreRepository("qualityChecks")
production_repo = FirestoreRepository("production")
order_repo = FirestoreRepository("orders")
employee_repo = FirestoreRepository("employees")

class QualityService:
    @staticmethod
    def create_quality_check(data, inspector_id=None, user_id=None, user_name=None):
        """
        Perform quality inspection in Cloud Firestore:
        - If Pass:
            - Production Quality Check stage = Completed
            - Production Packaging stage = In Progress
            - Order currentStage = Packaging
            - Notification & Audit log
        - If Fail:
            - Production Quality Check stage = Failed
            - Order status = Rework
            - Target rework stage reset to Rework
            - Notification & Audit log
        """
        order_id = data.get("orderId")
        order = order_repo.get_by_id(order_id)
        if not order:
            return None, "Order not found", "ORDER_NOT_FOUND"

        # Check Finishing completed
        order_stages = production_repo.get_all(filters={"orderId": order_id})
        finishing_stage = next((s for s in order_stages if s["stage"] == "Finishing"), None)
        if finishing_stage and finishing_stage.get("status") != "Completed":
            return None, "Cannot perform Quality Check before Finishing stage is Completed", "INVALID_WORKFLOW"

        qc_stage = next((s for s in order_stages if s["stage"] == "Quality Check"), None)
        packaging_stage = next((s for s in order_stages if s["stage"] == "Packaging"), None)

        actual_inspector_id = inspector_id or data.get("inspectorId", "EMP004")
        emp = employee_repo.get_by_id(actual_inspector_id)
        inspector_name = emp.get("name") if emp else data.get("inspectorName", "Quality Inspector")

        result = data.get("result", "Pass")
        now = get_current_timestamp()

        qc_id = data.get("qualityCheckId")
        if qc_id:
            qc_id = str(qc_id).strip()
            existing = quality_repo.get_by_id(qc_id)
            if existing:
                return None, f"Quality check with ID '{qc_id}' already exists", "DUPLICATE_QC"
        else:
            qc_count = quality_repo.count() + 1
            qc_id = f"QC{qc_count:03d}"

        qc_record = {
            "qualityCheckId": qc_id,
            "id": qc_id,
            "orderId": order_id,
            "inspectorId": actual_inspector_id,
            "inspectorName": inspector_name,
            "inspectionDate": data.get("inspectionDate") or now,
            "defectType": data.get("defectType", "None"),
            "defectQuantity": int(data.get("defectQuantity", 0)),
            "result": result,
            "remarks": data.get("remarks", "")
        }

        created_qc = quality_repo.create(qc_record, doc_id=qc_id)

        if result == "Pass":
            if qc_stage:
                production_repo.update(qc_stage["productionId"], {
                    "status": "Completed",
                    "progress": 100,
                    "completedQuantity": qc_stage.get("quantity", 0),
                    "completedDate": now,
                    "remarks": "Passed inspection: " + qc_record["remarks"]
                })

            if packaging_stage:
                production_repo.update(packaging_stage["productionId"], {
                    "status": "In Progress",
                    "startDate": now
                })

            order_repo.update(order_id, {
                "currentStage": "Packaging",
                "status": "In Production"
            })

            NotificationService.create_notification(
                user_id="ALL",
                notif_type="QUALITY",
                title="Quality Inspection Passed",
                message=f"Order {order_id} passed Quality Check and is ready for Packaging.",
                order_id=order_id
            )

            AuditService.log(
                user_id=user_id or actual_inspector_id,
                user_name=user_name or inspector_name,
                action="QUALITY_PASSED",
                entity_type="qualityChecks",
                entity_id=qc_id,
                description=f"Order {order_id} passed quality inspection by {inspector_name}."
            )
        else:
            # Result is Fail -> Rework
            if qc_stage:
                production_repo.update(qc_stage["productionId"], {
                    "status": "Failed",
                    "remarks": f"Failed with {qc_record['defectQuantity']} defects ({qc_record['defectType']})."
                })

            rework_stage_name = data.get("reworkStage", "Stitching")
            rework_stage = next((s for s in order_stages if s["stage"] == rework_stage_name), None)
            if rework_stage:
                production_repo.update(rework_stage["productionId"], {
                    "status": "Rework",
                    "remarks": f"Returned for rework: {qc_record['remarks']}"
                })

            order_repo.update(order_id, {
                "status": "Rework",
                "currentStage": rework_stage_name
            })

            NotificationService.create_notification(
                user_id="ALL",
                notif_type="QUALITY",
                title="Quality Inspection Failed",
                message=f"Order {order_id} failed Quality Check ({qc_record['defectType']}) and was sent to {rework_stage_name} for Rework.",
                order_id=order_id
            )

            AuditService.log(
                user_id=user_id or actual_inspector_id,
                user_name=user_name or inspector_name,
                action="QUALITY_FAILED",
                entity_type="qualityChecks",
                entity_id=qc_id,
                description=f"Order {order_id} failed inspection ({qc_record['defectType']}, {qc_record['defectQuantity']} units). Sent to {rework_stage_name} for Rework."
            )

        return created_qc, f"Quality check recorded: {result}", None

    @staticmethod
    def get_quality_checks(order_id=None):
        """Get all QC records or for a specific order."""
        filters = {}
        if order_id:
            filters["orderId"] = order_id
        return quality_repo.get_all(filters=filters, sort_by="inspectionDate", reverse=True)

    @staticmethod
    def get_quality_check_by_id(qc_id):
        """Get single QC record."""
        return quality_repo.get_by_id(qc_id)

    @staticmethod
    def update_quality_check(qc_id, update_data):
        """Update existing QC record."""
        qc = quality_repo.get_by_id(qc_id)
        if not qc:
            return None, "Quality check record not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["defectType", "defectQuantity", "remarks", "result"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        updated = quality_repo.update(qc_id, safe_updates)
        return updated, "Quality check updated successfully", None
