from dataclasses import dataclass


@dataclass
class Operator:
    id: int
    mo: str
    trade_name: str | None = None
    company_name: str | None = None
    email: str | None = None
    phone: str | None = None
    rfc_tax_id: str | None = None
    
@dataclass
class OperatorUserLink:
    id:int
    operator_id:int
    user_id:int
    
@dataclass
class OperatorsFiles:
    id:int
    operator_id: int
    type_file_id:int
    name: str
    url: str