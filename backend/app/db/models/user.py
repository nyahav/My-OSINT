# app/db/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base # Ensure this import path is correct
from datetime import datetime # Import datetime for default values
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Consistent naming with Python conventions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False) # Changed from 'admin' to 'is_admin' for consistency

    created_by = Column(String(255), nullable=True)
    created_date = Column(DateTime, default=datetime.now, nullable=True) # Use datetime.now for creation timestamp
    updated_by = Column(String(255), nullable=True)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True) # Use onupdate for update timestamp

    scans = relationship("Scan", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"