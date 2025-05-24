
from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base  # We'll define this below

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(128))
    first_name = Column(String(50))
    last_name = Column(String(50))
    admin = Column(Boolean, default=False)
