from .extensions import db
from .models import Role, User

DEFAULT_ROLES = ("ADMIN", "STARTUP_REP", "INVESTOR")


def initialize_database(seed_admin=False):
    db.create_all()

    existing_roles = {role.name for role in Role.query.all()}
    missing_roles = [Role(name=role_name) for role_name in DEFAULT_ROLES if role_name not in existing_roles]
    if missing_roles:
        db.session.add_all(missing_roles)
        db.session.commit()

    if seed_admin and not User.query.filter_by(email="admin@example.com").first():
        admin_role = Role.query.filter_by(name="ADMIN").first()
        if admin_role is not None:
            admin = User(
                role_id=admin_role.id,
                full_name="System Admin",
                email="admin@example.com",
                organization_name="Incubator HQ",
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.commit()
