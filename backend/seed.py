from app import create_app
from app.bootstrap import initialize_database

app = create_app()


with app.app_context():
    initialize_database(seed_admin=True)
    print("Seed data created")
