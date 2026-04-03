from app import create_app
from app.extensions import db
from app.models import Role, User

app = create_app()


with app.app_context():
    db.create_all()

    for role_name in ["ADMIN", "STARTUP_REP", "INVESTOR"]:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()

    admin_role = Role.query.filter_by(name="ADMIN").first()

    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(
            role_id=admin_role.id,
            full_name="System Admin",
            email="admin@example.com",
            organization_name="Incubator HQ",
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

    db.session.commit()
    print("Seed data created")
