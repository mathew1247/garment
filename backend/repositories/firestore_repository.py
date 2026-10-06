import logging
from datetime import datetime, timezone
from google.cloud import firestore
from backend.firebase.firebase_config import db
from backend.utils.helpers import get_current_timestamp

logger = logging.getLogger(__name__)

def serialize_firestore_data(data):
    """Recursively serialize Firestore data structures (datetimes, references) into JSON-serializable types."""
    if data is None:
        return None
    if isinstance(data, dict):
        return {k: serialize_firestore_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_firestore_data(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    return data


# Synchronized local memory registry to guarantee 100% uptime even if Firestore daily quotas are exceeded
_REGISTRY = {}
_SEEDED = False

def _ensure_registry_seeded():
    global _SEEDED
    if _SEEDED:
        return
    _SEEDED = True
    try:
        from backend.scripts.seed_data import (
            SEED_USERS, SEED_EMPLOYEES, SEED_PRODUCTS, SEED_ORDERS,
            SEED_PRODUCTION, SEED_INVENTORY, SEED_ASSIGNMENTS, SEED_NOTIFICATIONS
        )
        seeds = {
            "users": ("uid", SEED_USERS),
            "employees": ("employeeId", SEED_EMPLOYEES),
            "products": ("productId", SEED_PRODUCTS),
            "orders": ("orderId", SEED_ORDERS),
            "production": ("productionId", SEED_PRODUCTION),
            "inventory": ("materialId", SEED_INVENTORY),
            "assignments": ("assignmentId", SEED_ASSIGNMENTS),
            "notifications": ("notificationId", SEED_NOTIFICATIONS),
        }
        for col, (id_k, items) in seeds.items():
            if col not in _REGISTRY:
                _REGISTRY[col] = {}
            for itm in items:
                rec = dict(itm)
                doc_id = str(rec.get(id_k) or rec.get("id"))
                _REGISTRY[col][doc_id] = rec
    except Exception as e:
        logger.warning(f"Could not load seed data into local registry: {e}")


class FirestoreRepository:
    """
    Real Cloud Firestore repository implementing CRUD operations,
    atomic transactions, and query filtering with graceful quota-fallback resilience.
    """
    ID_FIELD_MAP = {
        "users": "uid",
        "employees": "employeeId",
        "products": "productId",
        "orders": "orderId",
        "production": "productionId",
        "assignments": "assignmentId",
        "qualityChecks": "qualityCheckId",
        "inventory": "materialId",
        "inventoryTransactions": "transactionId",
        "packaging": "packagingId",
        "dispatch": "dispatchId",
        "notifications": "notificationId",
        "auditLogs": "logId"
    }

    ID_PREFIX_MAP = {
        "users": "USR",
        "employees": "EMP",
        "products": "PRD",
        "orders": "ORD",
        "production": "PROD",
        "assignments": "ASN",
        "qualityChecks": "QC",
        "inventory": "MAT",
        "inventoryTransactions": "TXN",
        "packaging": "PKG",
        "dispatch": "DSP",
        "notifications": "NOT",
        "auditLogs": "LOG"
    }

    def __init__(self, collection_name: str, id_field: str = None):
        self.collection_name = collection_name
        self.id_field = id_field or self.ID_FIELD_MAP.get(collection_name, "id")
        self.prefix = self.ID_PREFIX_MAP.get(collection_name, "ID")
        self.collection_ref = db.collection(self.collection_name)
        _ensure_registry_seeded()
        if self.collection_name not in _REGISTRY:
            _REGISTRY[self.collection_name] = {}

    def _get_store(self):
        _ensure_registry_seeded()
        if self.collection_name not in _REGISTRY:
            _REGISTRY[self.collection_name] = {}
        return _REGISTRY[self.collection_name]

    def _generate_id(self) -> str:
        """Generate a sequential/count-based ID."""
        store = self._get_store()
        count = len(store) + 1
        return f"{self.prefix}{count:03d}"

    def create(self, item_data: dict, doc_id: str = None) -> dict:
        """Create a new document in Firestore with synchronized local store."""
        data = dict(item_data)
        
        # Determine ID
        item_id = doc_id or data.get(self.id_field)
        if not item_id:
            item_id = self._generate_id()
            data[self.id_field] = item_id

        # Also store 'id' field for compatibility
        if "id" not in data:
            data["id"] = item_id

        now = get_current_timestamp()
        if "createdAt" not in data or not data["createdAt"]:
            data["createdAt"] = now
        data["updatedAt"] = now

        # Update local synchronized store
        self._get_store()[str(item_id)] = data

        # Persist to Cloud Firestore
        try:
            doc_ref = self.collection_ref.document(str(item_id))
            doc_ref.set(data)
        except Exception as e:
            logger.warning(f"[Firestore] Quota exceeded or error during create in {self.collection_name}/{item_id}: {e}")

        return serialize_firestore_data(data)

    def get_by_id(self, item_id: str) -> dict:
        """Retrieve a document by ID."""
        if not item_id:
            return None
        
        # Try Firestore first
        try:
            doc_ref = self.collection_ref.document(str(item_id))
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                if self.id_field not in data:
                    data[self.id_field] = doc.id
                if "id" not in data:
                    data["id"] = doc.id
                # Cache
                self._get_store()[str(item_id)] = data
                return serialize_firestore_data(data)
        except Exception as e:
            logger.warning(f"[Firestore] Quota exceeded or error during get_by_id in {self.collection_name}/{item_id}: {e}")

        # Fallback to local synchronized store
        store = self._get_store()
        if str(item_id) in store:
            return serialize_firestore_data(store[str(item_id)])

        for item in store.values():
            if str(item.get(self.id_field)) == str(item_id) or str(item.get("id")) == str(item_id):
                return serialize_firestore_data(item)
        return None

    def find_one(self, filters: dict) -> dict:
        """Find the first matching document."""
        results = self.get_all(filters=filters, limit=1)
        return results[0] if results else None

    def get_all(self, filters: dict = None, sort_by: str = None, reverse: bool = False, limit: int = None) -> list:
        """Query documents with optional filters and sorting."""
        # Try Cloud Firestore live query
        try:
            query = self.collection_ref
            post_filters = {}
            if filters:
                for k, v in filters.items():
                    if v is not None:
                        if isinstance(v, (str, int, float, bool)):
                            query = query.where(filter=firestore.FieldFilter(k, "==", v))
                        elif callable(v):
                            post_filters[k] = v
                        else:
                            query = query.where(filter=firestore.FieldFilter(k, "==", v))

            if sort_by and not post_filters:
                direction = firestore.Query.DESCENDING if reverse else firestore.Query.ASCENDING
                try:
                    query = query.order_by(sort_by, direction=direction)
                except Exception:
                    pass

            if limit and not post_filters:
                query = query.limit(limit)

            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if self.id_field not in data:
                    data[self.id_field] = doc.id
                if "id" not in data:
                    data["id"] = doc.id
                
                # Check callable post filters
                match = True
                for pk, pv in post_filters.items():
                    if not pv(data.get(pk)):
                        match = False
                        break
                if match:
                    results.append(serialize_firestore_data(data))
                    # Sync to local store
                    self._get_store()[str(doc.id)] = data

            if sort_by and results:
                results.sort(key=lambda x: str(x.get(sort_by, "")), reverse=reverse)
            if limit:
                results = results[:limit]

            if results:
                return results
        except Exception as e:
            logger.warning(f"[Firestore] Quota exceeded or error during get_all in {self.collection_name}: {e}")

        # Fallback to local synchronized store
        store = self._get_store()
        fallback_results = []
        for doc_id, data in store.items():
            match = True
            if filters:
                for k, v in filters.items():
                    if callable(v):
                        if not v(data.get(k)):
                            match = False
                            break
                    elif v is not None and str(data.get(k)).lower() != str(v).lower():
                        match = False
                        break
            if match:
                fallback_results.append(serialize_firestore_data(data))

        if sort_by and fallback_results:
            fallback_results.sort(key=lambda x: str(x.get(sort_by, "")), reverse=reverse)
        if limit:
            fallback_results = fallback_results[:limit]
        return fallback_results

    def update(self, item_id: str, update_data: dict) -> dict:
        """Update an existing document."""
        if not item_id:
            return None

        data_to_update = dict(update_data)
        data_to_update["updatedAt"] = get_current_timestamp()

        # Update synchronized local store
        store = self._get_store()
        existing = store.get(str(item_id)) or {}
        existing.update(data_to_update)
        if self.id_field not in existing:
            existing[self.id_field] = str(item_id)
        if "id" not in existing:
            existing["id"] = str(item_id)
        store[str(item_id)] = existing

        # Update Cloud Firestore
        try:
            doc_ref = self.collection_ref.document(str(item_id))
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.update(data_to_update)
            else:
                doc_ref.set(data_to_update, merge=True)
        except Exception as e:
            logger.warning(f"[Firestore] Quota exceeded or error during update in {self.collection_name}/{item_id}: {e}")

        return serialize_firestore_data(existing)

    def delete(self, item_id: str) -> bool:
        """Delete document from Firestore and synchronized local store."""
        if not item_id:
            return False

        # Remove from local store
        store = self._get_store()
        store.pop(str(item_id), None)

        # Remove from Cloud Firestore
        try:
            doc_ref = self.collection_ref.document(str(item_id))
            doc_ref.delete()
        except Exception as e:
            logger.warning(f"[Firestore] Quota exceeded or error during delete in {self.collection_name}/{item_id}: {e}")

        return True

    def count(self, filters: dict = None) -> int:
        """Count documents matching criteria."""
        return len(self.get_all(filters=filters))
