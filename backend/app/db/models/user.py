
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base 
from datetime import datetime 
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

   
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False) 

    created_by = Column(String(255), nullable=True)
    created_date = Column(DateTime, default=datetime.now, nullable=True) 
    updated_by = Column(String(255), nullable=True)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True) 

    scans = relationship("Scan", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"