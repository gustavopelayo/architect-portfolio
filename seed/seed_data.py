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
from app.models.setting import SiteSetting, HeroImage

SEED_PHOTOS = Path(__file__).parent / "images" / "photos"
SEED_TECHNICAL = Path(__file__).parent / "images" / "technical"
UPLOADS = Path("app/static/uploads")

PROJECTS = [
    {
        "name": "Kyoto House — Courtyard Residence",
        "description": "A private residence in the Higashiyama district of Kyoto, designed around a central courtyard that captures the seasonal changes of the surrounding hills. The structure uses rammed earth and hand-carved cedar, with a roof silhouette that echoes the neighbouring temple roofs. Sliding shoji screens dissolve the boundary between interior and garden, allowing the house to breathe with the landscape.",
        "year": 2025,
        "location": "Kyoto, Japan",
        "is_featured": True,
        "images": [
            "28075505-2dad-4b35-ae40-0085c15bac96.jpeg",
            "f79f8d1b-3882-4faf-b9ae-95533f602906.jpeg",
            "d9f7e061-4c70-460f-9d8d-9cdb577478de.jpeg",
            "0688972f-2372-416e-ad1f-fec7219d2676.jpeg",
            "a93dc905-df98-4818-8493-5105807b1c21.jpeg",
        ],
        "technical": [
            "f1551cab-f242-4f31-a586-540443fd3ecb.pdf",
            "4fb38469-96d2-4faa-996a-a6c98f5693c8.pdf",
            "c5a2a7ee-e687-48b7-92cf-74642a1ac87e.pdf",
            "b89499f8-689a-4e51-a198-e96ea9dfb1f7.pdf",
            "7e034af1-c3ea-4452-9df2-6bd04f70bb5a.pdf",
            "61ef4b67-2f41-44db-a956-146f4b83f245.pdf",
            "9cf8e72c-3331-4b7d-876e-3b80f4b85a16.pdf",
        ],
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
            src = SEED_PHOTOS / fname
            if not src.exists():
                print(f"  WARNING: {src} not found, skipping")
                continue
            shutil.copy2(src, dest / fname)
            url = f"/static/uploads/{pid}/{fname}"
            crud_image.create_portfolio_image(db, pid, ImageCreate(image_url=url, caption=""))
            print(f"  Added image {fname} to '{p['name']}'")

        first_img = db.query(PortfolioImage).filter(PortfolioImage.portfolio_id == pid).order_by(PortfolioImage.id).first()
        if first_img:
            first_img.is_cover = True

        for fname in p["technical"]:
            src = SEED_TECHNICAL / fname
            if not src.exists():
                continue
            tech_dest = dest / "technical"
            tech_dest.mkdir(parents=True, exist_ok=True)
            if src.suffix.lower() == ".pdf":
                import fitz
                out_name = src.stem + ".png"
                doc = fitz.open(src)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                pix.save(str(tech_dest / out_name))
                doc.close()
            else:
                out_name = fname
                shutil.copy2(src, tech_dest / fname)
            url = f"/static/uploads/{pid}/technical/{out_name}"
            crud_image.create_technical_image(db, pid, ImageCreate(image_url=url, caption=""))
            print(f"  Added technical drawing {fname} to '{p['name']}'")

        print(f"  Created project: {p['name']}")

    existing_settings = {r.key for r in db.query(SiteSetting).all()}

    defaults = {
        "tagline": "Design is not only what we see, but what quietly transforms how we dwell.",
        "logo_path": "/static/logo.png",
        "contact_email": "dadamoura@cloud.com",
        "contact_phone": "+351 931 110 004",
        "contact_address": "Rua Augusta, 123\nLisbon, Portugal",
        "contact_blurb": "We would love to hear from you. Whether you have a project in mind or simply want to learn more about our studio, feel free to reach out.",
        "about_title": "About\nDaniel Moura",
        "about_body": "Design is not only what we see, but what quietly transforms how we dwell.\n\nDaniel Moura is an architecture practice with projects spanning residential, commercial, and cultural spaces. We create holistic concepts that translate context, functionality, and personality into structures that feel both effortless and refined.\n\nOur approach is rooted in detail: from the grand scale of spatial planning to the subtle nuances of materiality and light, each element is crafted to evoke a tactile and emotional response. Above all, our work seeks to create harmony \u2014 spaces that inspire, comfort, and endure.",
    }

    for key, value in defaults.items():
        if key not in existing_settings:
            db.add(SiteSetting(key=key, value=value))
            print(f"  Created setting: {key}")

    hero_count = db.query(HeroImage).count()
    if hero_count == 0:
        src = SEED_PHOTOS / "28075505-2dad-4b35-ae40-0085c15bac96.jpeg"
        if src.exists():
            hero_dir = UPLOADS / "hero"
            hero_dir.mkdir(parents=True, exist_ok=True)
            fname = f"hero_default{src.suffix}"
            shutil.copy2(src, hero_dir / fname)
            db.add(HeroImage(
                image_url=f"/static/uploads/hero/{fname}",
                caption="",
                sort_order=0,
            ))
            print("  Created default hero image")

    db.commit()
    db.close()
    print("Done seeding.")

if __name__ == "__main__":
    seed()
