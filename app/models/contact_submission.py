from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    created_at = Column(DateTime, default=_utcnow)
