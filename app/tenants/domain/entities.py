from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class TenantStatus(str, Enum):
    PENDING = "pending"
    PROVISIONING_DB_DONE = "provisioning_db_done"
    ACTIVE = "active"
    FAILED = "failed"
    
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    
@dataclass
class Tenant:
    id: str
    name: str
    domain: str
    db_name: str
    status: TenantStatus
    secret_ref: str | None = None
    error: str | None = None
    review_note: str | None = None
    prefix: str | None = None
    
@dataclass
class KeyDomainTenant:
    id: str
    key: str
    name: str
    created_at: str
    
@dataclass
class ApiKeyRecord:
    id: str
    tenant_id:str
    domain:str
    key_prefix: str
    key_hash: str
    is_active: bool
    last_used_at: str