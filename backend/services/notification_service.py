from backend.repositories.firestore_repository import FirestoreRepository

notification_repo = FirestoreRepository("notifications")

class NotificationService:
    @staticmethod
    def create_notification(user_id, notif_type, title, message, order_id=None):
        """Create and store a system notification in Cloud Firestore."""
        count = notification_repo.count() + 1
        notif_id = f"NOT{count:03d}"
        data = {
            "notificationId": notif_id,
            "id": notif_id,
            "userId": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "orderId": order_id,
            "isRead": False
        }
        return notification_repo.create(data, doc_id=notif_id)

    @staticmethod
    def get_notifications(user_id=None, is_read=None):
        """Retrieve notifications with optional user filter and read status."""
        filters = {}
        if user_id:
            filters["userId"] = user_id
        if is_read is not None:
            filters["isRead"] = is_read

        return notification_repo.get_all(filters=filters, sort_by="createdAt", reverse=True)

    @staticmethod
    def mark_as_read(notification_id):
        """Mark a single notification as read."""
        notif = notification_repo.get_by_id(notification_id)
        if not notif:
            return None
        return notification_repo.update(notification_id, {"isRead": True})

    @staticmethod
    def mark_all_as_read(user_id=None):
        """Mark all notifications as read."""
        filters = {"userId": user_id} if user_id else {}
        all_notifs = notification_repo.get_all(filters=filters)
        updated_count = 0
        for n in all_notifs:
            if not n.get("isRead"):
                nid = n.get("notificationId") or n.get("id")
                notification_repo.update(nid, {"isRead": True})
                updated_count += 1
        return updated_count
