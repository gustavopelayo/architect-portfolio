from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.image import PortfolioImage, TechnicalImage
from app.core.security import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create admin user if not exists
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),  # Password is less than 72 chars
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created")
    
    db.close()
    print("Database initialized successfully — run `python seed/seed_data.py` to add sample projects")

if __name__ == "__main__":
    init_db()