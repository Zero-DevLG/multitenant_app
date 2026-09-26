from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from app.core.database import ControlBase as Base
from datetime import datetime, timezone

class TenantModel(Base):
    __tablename__ = "tenants"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    db_name = Column(String(64), unique=True, nullable=False)
    status = Column(String(32), nullable=True)
    secret_ref = Column(String(255), nullable=True)
    error = Column(String(255), nullable=True)
    review_note = Column(Text, nullable=True)
    prefix = Column(String(10), nullable=True)


class DomainApiKeyModel(Base):
    __tablename__ = "domain_api_keys"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(12), nullable=False)
    key_hash = Column(String(255), nullable=False)
    
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)