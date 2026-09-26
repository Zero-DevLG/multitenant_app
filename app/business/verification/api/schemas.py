from pydantic import BaseModel
from typing import Any

class AddressPayload(BaseModel):
    address_type_id: int
    street: str
    ext_number: str | None = None
    int_number: str | None = None
    neighborhood: str | None = None
    city: str
    state: str
    zip_code: str
    country: str

class OverviewRequest(BaseModel):
    module_id: int | None = None
    section_id: int | None = None

class SaveFieldAnswerRequest(BaseModel):
    module: str
    section: str
    field_code: str
    value: str | None = None             
    type_file_id: int | None = None      
    url: str | None = None             
    name: str | None = None
    address: AddressPayload | None = None
    catalog_id: int | None = None
    
class SaveFieldAnswersBatchRequest(BaseModel):
    answers: list[SaveFieldAnswerRequest]
    
class BatchAnswerResult(BaseModel):
    field_code: str
    section: str
    status: str
    answer_id: int | None = None
    validation_state: str | None = None
    reason: str | None = None
    
class SavedFieldAnswersBatchResponse(BaseModel):
    total: int
    saved: int
    failed: int
    results: list[BatchAnswerResult]
    section_statuses: dict[str, str]
    

class SaveFieldAnswerResponse(BaseModel):
    answer_id: int
    field_code: str
    validation_state: str
    section_status: str    
    
class FieldOverview(BaseModel):
    code: str
    type: str
    required: bool
    value: Any | None = None
    validation_state:str
    observation: str | None = None
    
class SectionOverview(BaseModel):
    name: str
    required: bool
    status: str
    sections: list[FieldOverview]
    
class ModuleOverview(BaseModel):
    name:str
    required:bool
    status: str
    sections: list[SectionOverview]
    
class OperatorOverviewResponse(BaseModel):
    modules: list[ModuleOverview]