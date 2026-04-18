from app import app, db, User, init_db
with app.app_context():
    admin = User.query.filter_by(email='admin@college.com').first()
    if not admin:
        print("Seeding database...")
        init_db()
    else:
        print("Admin user already exists.")
        # Ensure password is correct and role is Admin
        admin.set_password('admin123')
        admin.role = 'Admin'
        db.session.commit()
        print("Admin user updated to standard test credentials.")
