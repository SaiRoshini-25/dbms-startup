from datetime import datetime

from flask import jsonify
from flask_jwt_extended import get_jwt

from .extensions import db
from .models import ActivityLog, Notification, StartupMember


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def error_response(message, status_code):
    return jsonify({"message": message}), status_code


def role_required(*allowed_roles):
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                return error_response("Forbidden", 403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_role():
    return get_jwt().get("role")


def get_startup_ids_for_user(user_id):
    rows = StartupMember.query.filter_by(user_id=user_id).all()
    return [row.startup_id for row in rows]


def user_owns_startup(user_id, startup_id):
    return StartupMember.query.filter_by(user_id=user_id, startup_id=startup_id).first() is not None


def create_notification(recipient_user_id, title, message, link=None):
    notification = Notification(
        recipient_user_id=recipient_user_id,
        title=title,
        message=message,
        link=link,
    )
    db.session.add(notification)
    return notification


def log_activity(actor_user_id, entity_type, entity_id, action_type, summary, old_values=None, new_values=None):
    log = ActivityLog(
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action_type=action_type,
        action_summary=summary,
        old_values=old_values,
        new_values=new_values,
    )
    db.session.add(log)


def recalculate_startup_totals(startup):
    approved_commitments = [commitment for commitment in startup.commitments if commitment.status == "APPROVED"]
    startup.total_raised = sum((commitment.approved_amount or 0) for commitment in approved_commitments)
    startup.equity_allocated = sum(commitment.equity_percentage or 0 for commitment in approved_commitments)
    startup.investor_count = len({commitment.investor_id for commitment in approved_commitments})
    if startup.total_raised <= 0:
        startup.funding_status = "BOOTSTRAPPED" if startup.funding_status == "BOOTSTRAPPED" else startup.funding_status
    elif startup.target_amount and startup.total_raised >= startup.target_amount:
        startup.funding_status = "FUNDED"
    else:
        startup.funding_status = "IN_PROGRESS"


def startup_accepting_investment(startup):
    has_equity_capacity = (startup.equity_allocated or 0) < 100
    has_amount_capacity = not startup.target_amount or (startup.total_raised or 0) < startup.target_amount
    return startup.is_published and startup.incubator_status not in {"FUNDED", "CLOSED"} and has_equity_capacity and has_amount_capacity


def refresh_startup_visibility(startup):
    if startup_accepting_investment(startup):
        startup.funding_status = startup.funding_status or "IN_PROGRESS"
        return startup

    startup.is_published = False
    startup.published_at = None
    if (startup.equity_allocated or 0) >= 100 or (startup.target_amount and (startup.total_raised or 0) >= startup.target_amount):
        startup.incubator_status = "FUNDED"
        startup.funding_status = "FUNDED"
    elif startup.funding_rounds:
        startup.incubator_status = "CLOSED"
    return startup
