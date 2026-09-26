from abc import ABC, abstractmethod
from app.business.verification.domain.entities import Modules, Sections, FieldRule, StatusRule
from .entities import Answer, ReferenceAnswer, Document, Address, AnswerHistoryEntry, FileDetail, AddressDetail

class VerificationRulesRepository(ABC):
    # Lectura para armar jerarquia 
    @abstractmethod
    async def get_all_modules(self) -> list[Modules]: ... 
    
    @abstractmethod
    async def get_module_by_name(self, name: str) -> Modules | None: ...
    
    @abstractmethod
    async def get_module_by_id(self, module_id: int) -> Modules | None: ...
    
    @abstractmethod
    async def get_module_by_code(self, code: str) -> Modules | None: ...
    
    @abstractmethod
    async def get_section_by_id(self, section_id: int) -> Sections | None: ...
    
    @abstractmethod
    async def get_section_by_name(self, module_id: int, name: str) -> Sections | None: ...
    
    @abstractmethod
    async def get_section_by_code(self, module_id: int, code: str) -> Sections | None: ...
    
    @abstractmethod
    async def get_field_rules(self, section_id: int) -> list[FieldRule]: ...
    
    @abstractmethod
    async def get_field_rule_by_code(self, section_id: int, code: str) -> FieldRule | None: ...
    
    async def get_section_status_rules(self, section_id: int) -> list[StatusRule]: ...
    
    @abstractmethod
    async def get_sections_by_module(self, module_id: int) -> list[Sections]: ...
    
    @abstractmethod
    async def get_module_status_rules(self, module_id: int) -> list[StatusRule]: ...
    
    # Escritura para script de sincronizacion
    @abstractmethod
    async def upsert_module(self, name:str, required: bool) -> Modules: ...
    
    @abstractmethod
    async def upsert_section(self, module_id: int, name: str, required: bool) -> Sections: ...
    
    @abstractmethod
    async def upsert_field_rule(self, section_id: int, code: str, type_:str, required: bool)-> FieldRule: ...
    
    @abstractmethod
    async def deactivate_field_rule(self, field_rule_id: int) -> None: ...
        
    
    @abstractmethod
    async def replace_section_status_rules(self, section_id: int, rules: list[dict]) -> None: ...
    
    @abstractmethod
    async def replace_module_status_rules(self, module_id: int, rules: list[dict]) -> None: ...
    
    
class VerificationAnswersRepository(ABC):
    # --- Lectura ---
    @abstractmethod
    async def get_answer(self, operator_id: int, field_rule_id: int) -> Answer | None: ...

    @abstractmethod
    async def get_answers_for_section(self, operator_id: int, section_id: int) -> list[Answer]: ...

    @abstractmethod
    async def get_history(self, answer_id: int) -> list[AnswerHistoryEntry]: ...
    
    @abstractmethod
    async def get_reference_answers_by_ids(self, ids:list[int]) -> dict[int, ReferenceAnswer]: ...
    
    
    # --- Escritura ---
    @abstractmethod
    async def save_text_answer(self, operator_id: int, field_rule_id: int, value: str) -> Answer: ...

    @abstractmethod
    async def save_file_answer(
        self, operator_id: int, field_rule_id: int,
        type_file_id: int, url: str, name: str | None,
    ) -> Answer: ...

    @abstractmethod
    async def save_address_answer(self, operator_id: int, field_rule_id: int, address_data: dict) -> Answer: ...

    @abstractmethod
    async def save_catalog_reference_answer(self, operator_id: int, field_rule_id: int, catalog_column: str, catalog_id: int): ...


    @abstractmethod
    async def evaluate_answer(
        self, answer_id: int, validation_state: str,
        observations: str | None, evaluated_by: str | None,
    ) -> Answer: ...
    
    
    # Consulta de respuestas
    @abstractmethod
    async def get_all_answers_for_operator(self, operator_id: int) -> list[Answer]: ...
    
    @abstractmethod
    async def get_files_by_ids(self, ids: list[int]) -> dict[int, "FileDetail"]: ...
    
    @abstractmethod
    async def get_addresses_by_ids(self, ids: list[int]) -> dict[int, "AddressDetail"]: ...
    
    