from datetime import date
from pathlib import Path
import sys
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.extensions import db
from app.models import Role, Startup, StartupMember, User


@pytest.fixture
def app():
    db_path = Path(__file__).resolve().parent / f"test-{uuid4().hex}.db"
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "JWT_SECRET_KEY": "test-secret-key-1234567890-test-secret-key",
        }
    )

    with test_app.app_context():
        db.create_all()

        roles = {}
        for role_name in ["ADMIN", "STARTUP_REP", "INVESTOR"]:
            role = Role(name=role_name)
            db.session.add(role)
            roles[role_name] = role
        db.session.commit()

        admin = User(role_id=roles["ADMIN"].id, full_name="Admin User", email="admin@test.com")
        admin.set_password("Password@123")
        investor = User(role_id=roles["INVESTOR"].id, full_name="Investor User", email="investor@test.com")
        investor.set_password("Password@123")
        startup_rep = User(role_id=roles["STARTUP_REP"].id, full_name="Startup Rep", email="rep@test.com")
        startup_rep.set_password("Password@123")
        db.session.add_all([admin, investor, startup_rep])
        db.session.commit()

        startup = Startup(
            name="Alpha Labs",
            domain="FinTech",
            funding_stage="Seed",
            founding_date=date(2024, 1, 1),
            team_size=8,
            funding_status="BOOTSTRAPPED",
            created_by=admin.id,
        )
        db.session.add(startup)
        db.session.commit()

        membership = StartupMember(startup_id=startup.id, user_id=startup_rep.id, member_role="Founder", is_primary_contact=True)
        db.session.add(membership)
        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        if db_path.exists():
            db_path.unlink()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def tokens(client):
    def login(email):
        response = client.post("/api/auth/login", json={"email": email, "password": "Password@123"})
        assert response.status_code == 200
        return response.get_json()["accessToken"]

    return {
        "admin": login("admin@test.com"),
        "investor": login("investor@test.com"),
        "startup_rep": login("rep@test.com"),
    }
