from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import Blueprint

from ..extensions import db
from ..models import Notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.get("")
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    notifications = (
        Notification.query.filter_by(recipient_user_id=user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return {"items": [notification.to_dict() for notification in notifications]}


@notifications_bp.put("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    user_id = int(get_jwt_identity())
    notification = Notification.query.filter_by(id=notification_id, recipient_user_id=user_id).first_or_404()
    db.session.delete(notification)
    db.session.commit()
    return {"message": "Notification removed after being read", "notificationId": notification_id}
