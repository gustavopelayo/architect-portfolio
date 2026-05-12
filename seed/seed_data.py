import shutil, os, sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal, engine, Base
from app.db.base import Base
from app.models.portfolio import Portfolio
from app.models.image import PortfolioImage, TechnicalImage
from app.schemas.portfolio import PortfolioCreate
from app.schemas.image import ImageCreate
from app.crud import portfolio as crud_portfolio
from app.crud import image as crud_image

SEED_IMAGES = Path(__file__).parent / "images"
UPLOADS = Path("app/static/uploads")

PROJECTS = [
    {
        "name": "Kyoto House — Courtyard Residence",
        "description": "A private residence in the Higashiyama district of Kyoto, designed around a central courtyard that captures the seasonal changes of the surrounding hills. The structure uses rammed earth and hand-carved cedar, with a roof silhouette that echoes the neighbouring temple roofs. Sliding shoji screens dissolve the boundary between interior and garden, allowing the house to breathe with the landscape.",
        "year": 2025,
        "location": "Kyoto, Japan",
        "is_featured": True,
        "images": ["09210756-c724-450f-a139-cd5823c875bb.jpg", "390a780f-125e-4044-bbf3-a74ed2068f75.jpg"],
        "technical": ["ccf47c27-a732-47a3-b5ec-d891a4a0b2f4.jpg", "ed09037f-dfc5-4857-bad9-14fc39d51d22.jpg", "63ae46f7-3ed7-4f53-9ae8-d79c252d729f.jpg"],
    },
]

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = {p.name for p in db.query(Portfolio).all()}

    for p in PROJECTS:
        if p["name"] in existing:
            print(f"  Skipping '{p['name']}' — already exists")
            continue

        portfolio = crud_portfolio.create_portfolio(db, PortfolioCreate(
            name=p["name"],
            description=p["description"],
            year=p["year"],
            location=p["location"],
            is_featured=p["is_featured"],
        ))

        pid = portfolio.id
        dest = UPLOADS / str(pid)
        dest.mkdir(parents=True, exist_ok=True)

        for fname in p["images"]:
            src = SEED_IMAGES / fname
            if not src.exists():
                print(f"  WARNING: {src} not found, skipping")
                continue
            shutil.copy2(src, dest / fname)
            url = f"/static/uploads/{pid}/{fname}"
            crud_image.create_portfolio_image(db, pid, ImageCreate(image_url=url, caption=""))
            print(f"  Added image {fname} to '{p['name']}'")

        for fname in p["technical"]:
            src = SEED_IMAGES / fname
            if not src.exists():
                continue
            shutil.copy2(src, dest / fname)
            url = f"/static/uploads/{pid}/{fname}"
            crud_image.create_technical_image(db, pid, ImageCreate(image_url=url, caption=""))
            print(f"  Added technical drawing {fname} to '{p['name']}'")

        print(f"  Created project: {p['name']}")

    db.close()
    print("Done seeding.")

if __name__ == "__main__":
    seed()
