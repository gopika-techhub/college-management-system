from app import app, db, init_db
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
if os.path.exists(db_path):
    print(f"Deleting {db_path}")
    os.remove(db_path)

with app.app_context():
    print(f"Creating tables in {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.create_all()
    init_db()
    print("Database initialized and seeded.")
