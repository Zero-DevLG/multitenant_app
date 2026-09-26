from pydantic import BaseModel, EmailStr

class OperatorPreRegisterData(BaseModel):
    mo: str
    operator_status_id: int
    operator_type_id: int
    operator_class_id: int
    trade_name: str | None = None
    company_name: str | None = None
    rfc_tax_id: str
    website: str | None = None
    email_fiscal_name: str | None = None
    cedula_fiscal_name:str | None = None
    email: str
    contact_name: str
    code_alfa: str | None = None
    code_num: str | None = None
    phone: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    
    
class Enterprises(BaseModel):
    id: int
    trade_name: str
    domain: str
    rfc: str
    
class BulkOperatorRegisterRequest(BaseModel):
    operator: OperatorPreRegisterData
    domains: list[Enterprises]

class OperatorRegisterResult(BaseModel):
    domain: str
    status: str
    operator_id: int | None = None
    reason: str | None = None
    
class BulkOperatorRegisterResponse(BaseModel):
    total: int
    created: int
    skipped: int
    failed: int
    results: list[OperatorRegisterResult]        
