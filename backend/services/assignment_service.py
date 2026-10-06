from backend.repositories.firestore_repository import FirestoreRepository
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.helpers import get_current_timestamp

assignment_repo = FirestoreRepository("assignments")
employee_repo = FirestoreRepository("employees")
order_repo = FirestoreRepository("orders")
production_repo = FirestoreRepository("production")

class AssignmentService:
    @staticmethod
    def create_assignment(data, user_id=None, user_name=None):
        """
        Assign an employee to a production task in Cloud Firestore:
        - Validates employee exists & is active
        - Validates order exists
        - Validates production stage exists
        - Updates production stage assignedEmployee
        - Creates assignment record
        - Sends notification & audit log
        """
        emp_id = data.get("employeeId")
        order_id = data.get("orderId")
        prod_id = data.get("productionId")

        emp = employee_repo.get_by_id(emp_id)
        if not emp:
            return None, "Employee not found", "EMPLOYEE_NOT_FOUND"

        if emp.get("status") != "Active":
            return None, "Cannot assign tasks to an inactive employee", "EMPLOYEE_INACTIVE"

        order = order_repo.get_by_id(order_id)
        if not order:
            return None, "Order not found", "ORDER_NOT_FOUND"

        stage = production_repo.get_by_id(prod_id)
        if not stage:
            return None, "Production stage not found", "STAGE_NOT_FOUND"

        if stage.get("orderId") != order_id:
            return None, "Production stage does not belong to specified order", "INVALID_ASSOCIATION"

        asn_id = data.get("assignmentId")
        if asn_id:
            asn_id = str(asn_id).strip()
            existing = assignment_repo.get_by_id(asn_id)
            if existing:
                return None, f"Assignment with ID '{asn_id}' already exists", "DUPLICATE_ASSIGNMENT"
        else:
            asn_count = assignment_repo.count() + 1
            asn_id = f"ASN{asn_count:03d}"
        now = get_current_timestamp()

        asn_record = {
            "assignmentId": asn_id,
            "id": asn_id,
            "employeeId": emp_id,
            "employeeName": emp.get("name"),
            "orderId": order_id,
            "productionId": prod_id,
            "stage": stage.get("stage"),
            "task": data.get("task", f"{stage.get('stage')} for {order.get('productName')}"),
            "quantity": int(data.get("quantity", stage.get("quantity", 0))),
            "assignedDate": data.get("assignedDate") or now,
            "expectedCompletion": data.get("expectedCompletion") or stage.get("expectedCompletion"),
            "status": data.get("status", "Assigned")
        }

        created_asn = assignment_repo.create(asn_record, doc_id=asn_id)

        # Update assigned employee on the production stage in Firestore
        production_repo.update(prod_id, {
            "assignedEmployeeId": emp_id,
            "assignedEmployeeName": emp.get("name")
        })

        NotificationService.create_notification(
            user_id="ALL",
            notif_type="ASSIGNMENT",
            title="Worker Assigned",
            message=f"{emp.get('name')} assigned to {stage.get('stage')} on Order {order_id}.",
            order_id=order_id
        )

        AuditService.log(
            user_id=user_id,
            user_name=user_name,
            action="WORKER_ASSIGNED",
            entity_type="assignments",
            entity_id=asn_id,
            description=f"Assigned worker {emp.get('name')} ({emp_id}) to {stage.get('stage')} for Order {order_id}."
        )

        return created_asn, "Worker assigned successfully", None

    @staticmethod
    def get_assignments(employee_id=None, order_id=None, status=None):
        """Retrieve assignments with optional filters."""
        filters = {}
        if employee_id:
            filters["employeeId"] = employee_id
        if order_id:
            filters["orderId"] = order_id
        if status:
            filters["status"] = status
        return assignment_repo.get_all(filters=filters, sort_by="assignedDate", reverse=True)

    @staticmethod
    def get_assignment_by_id(assignment_id):
        """Retrieve single assignment record."""
        return assignment_repo.get_by_id(assignment_id)

    @staticmethod
    def update_assignment(assignment_id, update_data):
        """Update assignment record."""
        asn = assignment_repo.get_by_id(assignment_id)
        if not asn:
            return None, "Assignment not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["task", "quantity", "expectedCompletion", "status"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        updated = assignment_repo.update(assignment_id, safe_updates)
        return updated, "Assignment updated successfully", None

    @staticmethod
    def delete_assignment(assignment_id):
        """Delete assignment."""
        asn = assignment_repo.get_by_id(assignment_id)
        if not asn:
            return False, "Assignment not found"
        return assignment_repo.delete(assignment_id), None
