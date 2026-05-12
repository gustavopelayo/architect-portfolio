from app.db.session import SessionLocal
from app.models.setting import SiteSetting, HeroImage


def get_site_settings():
    db = SessionLocal()
    try:
        rows = db.query(SiteSetting).all()
        settings = {r.key: r.value for r in rows}
        settings["hero_images"] = db.query(HeroImage).order_by(HeroImage.sort_order).all()
        return settings
    finally:
        db.close()
