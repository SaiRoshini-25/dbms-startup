from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import Role, User
from ..utils import error_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    required_fields = ["fullName", "email", "password", "role"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return error_response(f"Missing fields: {', '.join(missing)}", 400)

    role = Role.query.filter_by(name=data["role"]).first()
    if role is None or role.name not in {"STARTUP_REP", "INVESTOR"}:
        return error_response("Invalid registration role", 400)

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return error_response("Email already registered", 409)

    user = User(
        role_id=role.id,
        full_name=data["fullName"],
        email=data["email"],
        phone=data.get("phone"),
        organization_name=data.get("organizationName"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return {"message": "Registration successful", "user": user.to_dict()}, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.locked_until and user.locked_until > datetime.utcnow():
        return {"message": "Account locked. Try again later."}, 423

    if not user or not user.check_password(password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
        return {"message": "Invalid Credentials"}, 401

    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.name, "email": user.email},
    )
    return {"accessToken": token, "user": user.to_dict()}
