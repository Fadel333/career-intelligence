# skip_enum_migration.py
from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Drop enums first
    print("🔄 Dropping enum types...")
    db.session.execute(text("DROP TYPE IF EXISTS employmenttype CASCADE"))
    db.session.execute(text("DROP TYPE IF EXISTS jobstatus CASCADE"))
    db.session.execute(text("DROP TYPE IF EXISTS placementstatus CASCADE"))
    db.session.commit()
    print("✅ Enums dropped!")
    
    # Drop all tables
    print("🔄 Dropping all tables...")
    db.drop_all()
    print("✅ Tables dropped!")
    
    # Create all tables
    print("🔄 Creating all tables...")
    db.create_all()
    print("✅ Tables created!")
    
    print("🎉 Database reset complete!")