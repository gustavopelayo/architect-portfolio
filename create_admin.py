#!/usr/bin/env python3
"""Create admin user for testing"""
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email="admin@architect.com",
    username="admin",
    hashed_password=get_password_hash("admin123"),
    is_active=True
)
db.add(admin)
db.commit()
db.close()
print("Admin user created: username=admin, password=admin123")
