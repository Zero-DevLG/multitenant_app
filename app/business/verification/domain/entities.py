from dataclasses import dataclass
from datetime import datetime

@dataclass
class Modules:
    id: int
    name:str
    code:str
    required: bool
    
@dataclass
class Sections:
    id:int
    module_id:int
    name: str
    code:str
    required: bool
    
@dataclass
class FieldRule:
    id: int
    section_id: int
    code: str
    type: str
    required: bool
    active: bool
    
@dataclass
class StatusRule:
    id: int
    priority: int
    condition_name: str
    result_status: str
    



@dataclass
class Answer:
    id: int
    operator_id: int
    section_field_rule_id: int
    value_text: str | None
    reference_id: str | None
    validation_state: str        
    observations: str | None
    evaluated_by: str | None
    evaluated_at: datetime | None
    
@dataclass
class ReferenceAnswer:
    id:int
    file_id: int | None
    address_id: int | None
    legal_authority_role_id: int | None

@dataclass
class Document:
    id: int
    operator_id: int
    type_file_id: int
    url: str
    name: str | None

@dataclass
class Address:
    id: int
    operator_id: int
    address_type_id: int
    street: str
    ext_number: str | None
    int_number: str | None
    neighborhood: str | None
    city: str
    state: str
    zip_code: str
    country: str

@dataclass
class AnswerHistoryEntry:
    id: int
    validation_state: str
    observations: str | None
    evaluated_by: str | None
    recorded_at: datetime
    
@dataclass
class FileDetail:
    id: int
    type_file_id: int
    name: int
    url: str

@dataclass
class AddressDetail:
    id: int
    address_type_id: int
    street: str
    ext_number: str | None
    int_number: str | None
    neighborhood: str | None
    city: str
    state: str
    zip_code: str
    country: str