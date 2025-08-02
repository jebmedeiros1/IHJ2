from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database_postgresql import Base

class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "dbo"} 
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    access_level = Column(String(50), nullable=False, server_default='user')
    reset_token = Column(String(200), nullable=True, index=True)
    reset_expiration = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
