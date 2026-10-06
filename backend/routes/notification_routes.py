from flask import Blueprint, request, g
from backend.services.notification_service import NotificationService
from backend.utils.responses import success_response, list_response, error_response
from backend.utils.decorators import token_required

notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notification_bp.route("", methods=["GET"])
@token_required
def get_notifications():
    # Return user notifications or all if admin
    user_id = getattr(g, "current_user", {}).get("id")
    role = getattr(g, "current_user", {}).get("role")

    # If admin or manager, show all or user specific
    filter_user = None if role in ("Administrator", "Manager") else user_id
    notifs = NotificationService.get_notifications(user_id=filter_user)
    return list_response(data=notifs, count=len(notifs), message="Notifications retrieved")

@notification_bp.route("/unread", methods=["GET"])
@token_required
def get_unread_notifications():
    user_id = getattr(g, "current_user", {}).get("id")
    role = getattr(g, "current_user", {}).get("role")
    filter_user = None if role in ("Administrator", "Manager") else user_id

    notifs = NotificationService.get_notifications(user_id=filter_user, is_read=False)
    return list_response(data=notifs, count=len(notifs), message="Unread notifications retrieved")

@notification_bp.route("/<notification_id>/read", methods=["PUT"])
@token_required
def mark_read(notification_id):
    updated = NotificationService.mark_as_read(notification_id)
    if not updated:
        return error_response("Notification not found", "NOT_FOUND", 404)
    return success_response(data=updated, message="Notification marked as read")

@notification_bp.route("/read-all", methods=["POST"])
@token_required
def mark_all_read():
    user_id = getattr(g, "current_user", {}).get("id")
    count = NotificationService.mark_all_as_read(user_id=user_id)
    return success_response(data={"markedCount": count}, message=f"Marked {count} notifications as read")
