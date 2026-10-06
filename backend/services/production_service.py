from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp
from backend.utils.validators import VALID_PRODUCTION_STAGES

production_repo = FirestoreRepository("production")
order_repo = FirestoreRepository("orders")
employee_repo = FirestoreRepository("employees")

class ProductionService:
    @staticmethod
    def get_production_records(order_id=None, stage=None, status=None, employee_id=None):
        """Retrieve production stages from Firestore with flexible filtering."""
        filters = {}
        if order_id:
            filters["orderId"] = order_id
        if stage:
            filters["stage"] = stage
        if status:
            filters["status"] = status
        if employee_id:
            filters["assignedEmployeeId"] = employee_id

        return production_repo.get_all(filters=filters, sort_by="productionId")

    @staticmethod
    def get_production_by_id(production_id):
        """Retrieve single production stage record."""
        return production_repo.get_by_id(production_id)

    @staticmethod
    def start_stage(production_id, employee_id=None, remarks=None, user_id=None, user_name=None):
        """
        Start a production stage:
        1. Validate sequence: preceding stage must be Completed
        2. Set status to 'In Progress', set startDate
        3. Update order currentStage
        4. Create notification
        5. Create audit log
        """
        stage_record = production_repo.get_by_id(production_id)
        if not stage_record:
            return None, "Production record not found", "NOT_FOUND"

        order_id = stage_record["orderId"]
        current_stage_name = stage_record["stage"]
        current_idx = VALID_PRODUCTION_STAGES.index(current_stage_name)

        # Strict sequence enforcement
        if current_idx > 0:
            all_order_stages = production_repo.get_all(filters={"orderId": order_id})
            prev_stage_name = VALID_PRODUCTION_STAGES[current_idx - 1]
            prev_stage = next((s for s in all_order_stages if s["stage"] == prev_stage_name), None)

            if prev_stage and prev_stage.get("status") != "Completed":
                return None, f"Cannot start {current_stage_name}. Previous stage '{prev_stage_name}' must be Completed first.", "INVALID_SEQUENCE"

        update_data = {
            "status": "In Progress",
            "startDate": stage_record.get("startDate") or get_current_timestamp()
        }
        if remarks:
            update_data["remarks"] = remarks

        if employee_id:
            emp = employee_repo.get_by_id(employee_id)
            if emp:
                update_data["assignedEmployeeId"] = employee_id
                update_data["assignedEmployeeName"] = emp.get("name")

        updated = production_repo.update(production_id, update_data)

        # Update order currentStage and status in Firestore
        order_repo.update(order_id, {
            "currentStage": current_stage_name,
            "status": "In Production"
        })

        NotificationService.create_notification(
            user_id="ALL",
            notif_type="PRODUCTION",
            title=f"Stage Started: {current_stage_name}",
            message=f"Production stage '{current_stage_name}' for Order {order_id} has started.",
            order_id=order_id
        )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="PRODUCTION_STARTED",
            entity_type="production",
            entity_id=production_id,
            description=f"Started stage '{current_stage_name}' for Order {order_id}."
        )

        return updated, "Stage started successfully", None

    @staticmethod
    def complete_stage(production_id, completed_quantity=None, remarks=None, user_id=None, user_name=None):
        """
        Complete a production stage:
        1. Verify current stage is In Progress
        2. Mark Completed
        3. Transition subsequent stage
        4. Update order status and currentStage
        5. Create notification
        6. Create audit log
        """
        stage_record = production_repo.get_by_id(production_id)
        if not stage_record:
            return None, "Production record not found", "NOT_FOUND"

        if stage_record.get("status") == "Completed":
            return None, "This production stage is already completed", "ALREADY_COMPLETED"

        order_id = stage_record["orderId"]
        current_stage_name = stage_record["stage"]
        current_idx = VALID_PRODUCTION_STAGES.index(current_stage_name)
        now = get_current_timestamp()

        final_qty = completed_quantity if completed_quantity is not None else stage_record.get("quantity", 0)

        update_payload = {
            "status": "Completed",
            "completedQuantity": final_qty,
            "progress": 100,
            "completedDate": now
        }
        if remarks:
            update_payload["remarks"] = remarks

        updated_stage = production_repo.update(production_id, update_payload)

        # Sequence advancement
        next_stage_name = None
        if current_idx + 1 < len(VALID_PRODUCTION_STAGES):
            next_stage_name = VALID_PRODUCTION_STAGES[current_idx + 1]
            all_order_stages = production_repo.get_all(filters={"orderId": order_id})
            next_stage = next((s for s in all_order_stages if s["stage"] == next_stage_name), None)

            # Auto-advance for cutting -> stitching -> finishing -> quality check
            if next_stage and current_stage_name in ("Cutting", "Stitching", "Finishing"):
                production_repo.update(next_stage["productionId"], {
                    "status": "In Progress",
                    "startDate": now
                })
                order_repo.update(order_id, {
                    "currentStage": next_stage_name
                })
        else:
            # All stages completed
            order_repo.update(order_id, {
                "status": "Completed",
                "currentStage": "Completed"
            })

        NotificationService.create_notification(
            user_id="ALL",
            notif_type="PRODUCTION",
            title=f"Stage Completed: {current_stage_name}",
            message=f"Stage '{current_stage_name}' for Order {order_id} marked as Completed." +
                    (f" Next stage: {next_stage_name}" if next_stage_name else " All stages complete!"),
            order_id=order_id
        )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="PRODUCTION_COMPLETED",
            entity_type="production",
            entity_id=production_id,
            description=f"Completed stage '{current_stage_name}' for Order {order_id} ({final_qty} units)."
        )

        return updated_stage, f"Stage '{current_stage_name}' completed successfully", None

    @staticmethod
    def update_production(production_id, update_data):
        """Update fields like progress, quantity, remarks, assigned employee."""
        stage_record = production_repo.get_by_id(production_id)
        if not stage_record:
            return None, "Production record not found", "NOT_FOUND"

        safe_updates = {}
        for k in ["completedQuantity", "progress", "remarks", "expectedCompletion", "status"]:
            if k in update_data:
                safe_updates[k] = update_data[k]

        if "assignedEmployeeId" in update_data:
            emp = employee_repo.get_by_id(update_data["assignedEmployeeId"])
            if emp:
                safe_updates["assignedEmployeeId"] = emp["employeeId"]
                safe_updates["assignedEmployeeName"] = emp["name"]

        updated = production_repo.update(production_id, safe_updates)
        return updated, "Production stage updated", None
