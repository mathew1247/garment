from backend.repositories.firestore_repository import FirestoreRepository
from backend.utils.helpers import get_current_timestamp

audit_repo = FirestoreRepository("auditLogs")

class AuditService:
    @staticmethod
    def log(user_id, user_name, action, entity_type, entity_id, description):
        """Record an entry in the Firestore auditLogs collection."""
        try:
            log_count = audit_repo.count() + 1
            log_id = f"LOG{log_count:04d}"
            entry = {
                "logId": log_id,
                "userId": user_id or "SYSTEM",
                "userName": user_name or "System Process",
                "action": action,
                "entityType": entity_type,
                "entityId": entity_id,
                "description": description,
                "timestamp": get_current_timestamp()
            }
            return audit_repo.create(entry, doc_id=log_id)
        except Exception as e:
            print(f"[AuditService Error] Failed to write audit log: {e}")
            return None
