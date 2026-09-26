from sqlalchemy import (
    Column, 
    String, 
    Integer,
    ForeignKey,
    DateTime
)
from datetime import datetime, timezone
from app.core.database import BusinessBase as Base

class User(Base):
    __tablename__= "users"
    id = Column(Integer,primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    name = Column(String(150),nullable=False)
    second_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=False)
    second_last_name = Column(String(150), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email_verified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    phone_wa = Column(String(12), nullable=False)
    status_id = Column(Integer, ForeignKey("catalog_user_statuses.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    
    
class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
class CatalogUserStatuses(Base):
    __tablename__ = "catalog_user_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))