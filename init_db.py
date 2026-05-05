from app.db.session import engine, SessionLocal, Base
from app.models.user import User
from app.models.portfolio import Portfolio
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
    
    # Create sample portfolio if not exists
    sample_portfolio = db.query(Portfolio).filter(Portfolio.name == "Sample Project").first()
    if not sample_portfolio:
        sample_portfolio = Portfolio(
            name="Sample Project",
            description="This is a sample architectural project to demonstrate the portfolio functionality.",
            year=2023,
            location="Sample City",
            is_featured=True
        )
        db.add(sample_portfolio)
        db.commit()
        print("Sample portfolio created")
    
    db.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    init_db()