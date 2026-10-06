class EmployeeModel:
    @staticmethod
    def to_dict(employee_id, name, department, role, phone, email, status="Active", created_at=None, updated_at=None):
        return {
            "employeeId": employee_id,
            "name": name,
            "department": department,
            "role": role,
            "phone": phone,
            "email": email,
            "status": status,
            "createdAt": created_at,
            "updatedAt": updated_at
        }
