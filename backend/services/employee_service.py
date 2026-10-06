from backend.repositories.firestore_repository import FirestoreRepository

employee_repo = FirestoreRepository("employees")
assignment_repo = FirestoreRepository("assignments")
production_repo = FirestoreRepository("production")
quality_repo = FirestoreRepository("qualityChecks")

class EmployeeService:
    @staticmethod
    def create_employee(data):
        """Create new employee in Cloud Firestore."""
        emp_id = data.get("employeeId")
        if emp_id:
            emp_id = str(emp_id).strip()
            existing = employee_repo.get_by_id(emp_id)
            if existing:
                return None, f"Employee with ID '{emp_id}' already exists"
        else:
            count = employee_repo.count() + 1
            emp_id = f"EMP{count:03d}"

        emp_record = {
            "employeeId": emp_id,
            "id": emp_id,
            "name": data.get("name", "").strip(),
            "department": data.get("department", "").strip(),
            "role": data.get("role", "").strip(),
            "phone": data.get("phone", "").strip(),
            "email": data.get("email", "").strip(),
            "profileImage": data.get("profileImage", ""),
            "status": data.get("status", "Active")
        }
        return employee_repo.create(emp_record, doc_id=emp_id), None

    @staticmethod
    def get_employees(department=None, role=None, status=None):
        """Retrieve employees with optional filters."""
        filters = {}
        if department:
            filters["department"] = department
        if role:
            filters["role"] = role
        if status:
            filters["status"] = status

        return employee_repo.get_all(filters=filters, sort_by="name")

    @staticmethod
    def get_employee_by_id(employee_id):
        """Retrieve single employee."""
        return employee_repo.get_by_id(employee_id)

    @staticmethod
    def update_employee(employee_id, update_data):
        """Update employee details."""
        emp = employee_repo.get_by_id(employee_id)
        if not emp:
            return None, "Employee not found", "NOT_FOUND"

        safe_updates = {}
        for f in ["name", "department", "role", "phone", "email", "profileImage", "status"]:
            if f in update_data:
                safe_updates[f] = update_data[f]

        updated = employee_repo.update(employee_id, safe_updates)
        return updated, "Employee updated successfully", None

    @staticmethod
    def delete_employee(employee_id):
        """Delete employee."""
        emp = employee_repo.get_by_id(employee_id)
        if not emp:
            return False, "Employee not found"
        return employee_repo.delete(employee_id), None

    @staticmethod
    def get_employee_performance(employee_id):
        """
        Calculate employee performance metrics from Firestore data:
        - completedTasks
        - pendingTasks
        - completedQuantity
        - assignedQuantity
        - completionPercentage
        - qualityScore
        - performanceStatus ('Excellent', 'Good', 'Average', 'Needs Improvement')
        """
        emp = employee_repo.get_by_id(employee_id)
        if not emp:
            return None, "Employee not found", "NOT_FOUND"

        assignments = assignment_repo.get_all(filters={"employeeId": employee_id})
        prod_stages = production_repo.get_all(filters={"assignedEmployeeId": employee_id})

        completed_tasks = 0
        pending_tasks = 0
        assigned_qty = 0
        completed_qty = 0

        for stage in prod_stages:
            qty = stage.get("quantity", 0)
            c_qty = stage.get("completedQuantity", 0)
            assigned_qty += qty
            completed_qty += c_qty
            if stage.get("status") == "Completed":
                completed_tasks += 1
            else:
                pending_tasks += 1

        for asn in assignments:
            if asn.get("status") == "Completed" and not any(s.get("productionId") == asn.get("productionId") for s in prod_stages):
                completed_tasks += 1
            elif asn.get("status") != "Completed" and not any(s.get("productionId") == asn.get("productionId") for s in prod_stages):
                pending_tasks += 1

        total_tasks = completed_tasks + pending_tasks
        completion_pct = round((completed_qty / assigned_qty * 100) if assigned_qty > 0 else (100 if total_tasks == 0 else 0), 1)

        qc_inspections = quality_repo.get_all(filters={"inspectorId": employee_id})
        if qc_inspections:
            passed = sum(1 for q in qc_inspections if q.get("result") == "Pass")
            quality_score = round((passed / len(qc_inspections)) * 100, 1)
        else:
            quality_score = 95.0

        if completion_pct >= 85 and quality_score >= 90:
            status_text = "Excellent"
        elif completion_pct >= 70 and quality_score >= 80:
            status_text = "Good"
        elif completion_pct >= 50:
            status_text = "Average"
        else:
            status_text = "Needs Improvement"

        performance_data = {
            "employeeId": employee_id,
            "name": emp.get("name"),
            "department": emp.get("department"),
            "completedTasks": completed_tasks,
            "pendingTasks": pending_tasks,
            "completedQuantity": completed_qty,
            "assignedQuantity": assigned_qty,
            "completionPercentage": completion_pct,
            "qualityScore": quality_score,
            "performanceStatus": status_text
        }

        return performance_data, "Performance retrieved", None
