from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.business.verification.domain.repository import VerificationRulesRepository
from app.business.verification.domain.entities import Modules, Sections, FieldRule, StatusRule, Answer, ReferenceAnswer
from app.business.verification.infrastructure.models import (
    Modules as ModuleModel,
    Sections as SectionModel,
    SectionFieldRuleModel,
    SectionStatusRuleModel,
    ModuleStatusRuleModel,
    OperatorFieldAnswerModel,
    OperatorFieldAnswerHistoryModel,
    ReferenceAnswerModel,
    SectionFieldFileTypeModel
)

from app.business.operators.models.model import CatalogTypeFiles

from app.business.verification.domain.repository import VerificationAnswersRepository
from app.business.verification.domain.entities import Answer, Document, Address, AnswerHistoryEntry, FileDetail, AddressDetail

from app.business.operators.models.model import OperatorsFiles as OperatorDocumentModel
from app.business.operators.models.model import OperatorAddressModel

from datetime import datetime, timezone

def _answer_to_entity(a: OperatorFieldAnswerModel) -> Answer:
    return Answer(
        id=a.id, operator_id=a.operator_id, section_field_rule_id=a.section_field_rule_id,
        value_text=a.value_text, reference_id=a.reference_id,
        validation_state=a.validation_state, observations=a.observations,
        evaluated_by=a.evaluated_by, evaluated_at=a.evaluated_at
    )
    
def _reference_answer_to_entity(r:ReferenceAnswerModel) -> ReferenceAnswer:
    return ReferenceAnswer(id=r.id, file_id=r.file_id, address_id=r.address_id, legal_authority_role_id=r.legal_authority_role_id, )


def _module_to_entity(m: ModuleModel) -> Modules:
    return Modules(id=m.id, name=m.name, code=m.code, required=m.required)

def _section_to_entity(s: SectionModel) -> Sections:
    return Sections(id=s.id, module_id=s.module_id, name=s.name, code=s.code, required=s.required)

def _field_rule_to_entity(f: SectionFieldRuleModel) -> FieldRule:
    return FieldRule(id=f.id, section_id=f.section_id, code=f.code, type=f.type, required=f.required, active=f.active)
    
def _status_rule_to_entity(r)-> StatusRule:
    return StatusRule(id=r.id, priority=r.priority, condition_name=r.condition_name,result_status=r.result_status)


class SqlAlchemyVerificationRuleRepository(VerificationRulesRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        
    # Lectura
    
    async def get_catalog_type_file_by_key(self, key: str) -> int | None:
        result = await self._session.execute(select(CatalogTypeFiles.id).where(CatalogTypeFiles.key==key))
        return result.scalar_one_or_none()
    
    async def get_field_file_types(self, field_rule_id: int) -> dict:
        result = await self._session.execute(
            select(CatalogTypeFiles).join(SectionFieldFileTypeModel, SectionFieldFileTypeModel.catalog_type_file_id ==CatalogTypeFiles.id).where(SectionFieldFileTypeModel.section_field_rule_id == field_rule_id)
        )
        data = result.scalar_one_or_none()
        return {"id": data.id, "key": data.key, "name": data.name} 
    
    async def get_module_by_id(self, module_id: int) -> Modules:
        result = await self._session.execute(select(ModuleModel).where(ModuleModel.id == module_id))
        m = result.scalar_one_or_none()
        return _module_to_entity(m) if m else None
    
    async def get_all_modules(self):
        result = await self._session.execute(select(ModuleModel))
        return [_module_to_entity(m) for m in result.scalars()]
    
    async def get_module_by_name(self, name: str) -> Modules:
        result = await self._session.execute(select(ModuleModel).where(ModuleModel.name == name))
        m = result.scalar_one_or_none()
        return _module_to_entity(m) if m else None
    
    async def get_module_by_code(self, code: str) -> Modules:
        result = await self._session.execute(select(ModuleModel).where(ModuleModel.code == code))
        m = result.scalar_one_or_none()
        return _module_to_entity(m) if m else None
    
    async def get_section_by_id(self, section_id: int) -> Sections:
        result = await self._session.execute(select(SectionModel).where(SectionModel.id == section_id))
        s = result.scalar_one_or_none()
        return _section_to_entity(s) if s else None
    
    async def get_section_by_name(self, module_id: int, name:str) -> Sections | None:
        result = await self._session.execute(
            select(SectionModel).where(SectionModel.module_id == module_id, SectionModel.name == name)
        )
        s = result.scalar_one_or_none()
        return _section_to_entity(s) if s else None
    
    async def get_section_by_code(self, module_id: int, code: str)-> Sections | None:
        result = await self._session.execute(
            select(SectionModel).where(SectionModel.module_id == module_id, SectionModel.code == code)
        )
        s = result.scalar_one_or_none()
        return _section_to_entity(s) if s else None
    
    async def get_sections_by_module(self, module_id: int) -> list[Sections] :
        result = await self._session.execute(select(SectionModel).where(SectionModel.module_id == module_id))
        return [_section_to_entity(s) for s in result.scalars()]
    
    async def get_field_rules(self, section_id: int) -> list[FieldRule]:
        result = await self._session.execute(
            select(SectionFieldRuleModel).where(
                SectionFieldRuleModel.section_id == section_id,
                SectionFieldRuleModel.active == True,
            )
        )
        return [_field_rule_to_entity(f) for f in result.scalars()]
    
    
    async def get_field_rule_by_code(self, section_id: int, code: str):
        result = await self._session.execute(
            select(SectionFieldRuleModel).where(
                SectionFieldRuleModel.section_id == section_id,
                SectionFieldRuleModel.code == code,
                SectionFieldRuleModel.active == True,
            )
        )
        f = result.scalar_one_or_none()
        return _field_rule_to_entity(f) if f else None
    
    async def get_section_status_rules(self, section_id:int):
        result = await self._session.execute(
            select(SectionStatusRuleModel)
            .where(SectionStatusRuleModel.section_id == section_id)
            .order_by(SectionStatusRuleModel.priority)
        )
        return [_status_rule_to_entity(r) for r in result.scalars()]
    
    async def get_module_status_rules(self, module_id: int):
        result = await self._session.execute(
            select(ModuleStatusRuleModel)
            .where(ModuleStatusRuleModel.module_id == module_id)
            .order_by(ModuleStatusRuleModel.priority)
        )
        return [_status_rule_to_entity(r) for r in result.scalars()]
    
    # Escritura 
    
    async def replace_field_file_types(self, field_rule_id: int, catalog_type_file_ids: int):
        await self._session.execute(
            delete(SectionFieldFileTypeModel).where(SectionFieldFileTypeModel.section_field_rule_id == field_rule_id)
        )
        
        for catalog_id in catalog_type_file_ids:
            self._session.add(SectionFieldFileTypeModel(section_field_rule_id=field_rule_id, catalog_type_file_id=catalog_id))
        await self._session.flush()
    
    
    async def upsert_module(self, name: str, code: str, required: bool) -> Modules:
        existing = await self.get_module_by_code(code)
        if existing:
            model = await self._session.get(ModuleModel, existing.id)
            model.required = required
            await self._session.flush()
            return _module_to_entity(model)
        model = ModuleModel(name=name, required=required, status_id=1)
        self._session.add(model)
        await self._session.flush()
        return _module_to_entity(model)
    
    async def upsert_section(self, module_id: int, code: str, name: str, required: bool) -> Sections:
        existing = await self.get_section_by_code(module_id, code)
        print(f"result: {existing}")
        if existing:
            model = await self._session.get(SectionModel, existing.id)
            model.required = required
            await self._session.flush()
            return _section_to_entity(model)
        model = SectionModel(module_id=module_id, name=name, required=required, status_id=1, code=code)
        self._session.add(model)
        await self._session.flush()
        print(f"{_section_to_entity(model)}")
        return _section_to_entity(model)
    
    async def upsert_field_rule(self, section_id: int, code: str, type_: str, required: bool) -> FieldRule:
        existing = await self.get_field_rule_by_code(section_id, code)
        print(f"field_exist: {existing}")
        if existing:
            model = await self._session.get(SectionFieldRuleModel, existing.id)
            model.type = type_
            model.required = required
            model.active = True   # por si se había desactivado y ahora reaparece en el YAML
            await self._session.flush()
            return _field_rule_to_entity(model)
        print(f"datos: {section_id}, {code}, {type_}, {required}")
        model = SectionFieldRuleModel(section_id=section_id, code=code, type=type_, required=required, active=True)
        print(f"model_raw{model.__dict__}")
        self._session.add(model)
        await self._session.flush()
        print(f"model:{_field_rule_to_entity(model)}")
        return _field_rule_to_entity(model)
    
    
    async def deactivate_field_rule(self, field_rule_id: int) -> None:
        model = await self._session.get(SectionFieldRuleModel, field_rule_id)
        if model:
            model.active = False
            await self._session.flush()
            
            
    async def replace_section_status_rules(self, section_id: int, rules: list[dict]) -> None:
        await self._session.execute(delete(SectionStatusRuleModel).where(SectionStatusRuleModel.section_id == section_id))
        for i, rule in enumerate(rules):
            self._session.add(SectionStatusRuleModel(
                section_id=section_id, priority=i, condition_name=rule["when"], result_status=rule["result"],
            ))
        await self._session.flush()

    async def replace_module_status_rules(self, module_id: int, rules: list[dict]) -> None:
        await self._session.execute(delete(ModuleStatusRuleModel).where(ModuleStatusRuleModel.module_id == module_id))
        for i, rule in enumerate(rules):
            self._session.add(ModuleStatusRuleModel(
                module_id=module_id, priority=i, condition_name=rule["when"], result_status=rule["result"],
            ))
        await self._session.flush()
        
        
def _answer_to_entity(a: OperatorFieldAnswerModel) -> Answer:
    return Answer(
        id=a.id, operator_id=a.operator_id, section_field_rule_id=a.section_field_rule_id,
        value_text=a.value_text, reference_id=a.reference_id,
        validation_state=a.validation_state, observations=a.observations,
        evaluated_by=a.evaluated_by, evaluated_at=a.evaluated_at,
    )


class SqlAlchemyVerificationAnswersRepository(VerificationAnswersRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_or_new_answer(self, operator_id: int, field_rule_id: int) -> OperatorFieldAnswerModel:
        result = await self._session.execute(
            select(OperatorFieldAnswerModel).where(
                OperatorFieldAnswerModel.operator_id == operator_id,
                OperatorFieldAnswerModel.section_field_rule_id == field_rule_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        model = OperatorFieldAnswerModel(
            operator_id=operator_id, section_field_rule_id=field_rule_id,
            validation_state="pending_verification",
        )
        self._session.add(model)
        return model

    # --- Lectura ---

    async def get_answer(self, operator_id: int, field_rule_id: int) -> Answer | None:
        result = await self._session.execute(
            select(OperatorFieldAnswerModel).where(
                OperatorFieldAnswerModel.operator_id == operator_id,
                OperatorFieldAnswerModel.section_field_rule_id == field_rule_id,
            )
        )
        model = result.scalar_one_or_none()
        return _answer_to_entity(model) if model else None

    async def get_answers_for_section(self, operator_id: int, section_id: int) -> list[Answer]:
        from .models import SectionFieldRuleModel   # import local para evitar ciclo con el repo de reglas
        result = await self._session.execute(
            select(OperatorFieldAnswerModel)
            .join(SectionFieldRuleModel, SectionFieldRuleModel.id == OperatorFieldAnswerModel.section_field_rule_id)
            .where(
                OperatorFieldAnswerModel.operator_id == operator_id,
                SectionFieldRuleModel.section_id == section_id,
            )
        )
        return [_answer_to_entity(a) for a in result.scalars()]

    async def get_history(self, answer_id: int) -> list[AnswerHistoryEntry]:
        result = await self._session.execute(
            select(OperatorFieldAnswerHistoryModel)
            .where(OperatorFieldAnswerHistoryModel.operator_field_answer_id == answer_id)
            .order_by(OperatorFieldAnswerHistoryModel.recorded_at)
        )
        return [
            AnswerHistoryEntry(
                id=h.id, validation_state=h.validation_state, observations=h.observations,
                evaluated_by=h.evaluated_by, recorded_at=h.recorded_at,
            )
            for h in result.scalars()
        ]
        
    async def get_reference_answers_by_ids(self, ids: list[int]) -> dict[int, ReferenceAnswer]:
        if not ids:
            return {}
        result = await self._session.execute(select(ReferenceAnswerModel).where(ReferenceAnswerModel.id.in_(ids)))
        return {r.id: _reference_answer_to_entity(r) for r in result.scalars().all()}

    # --- Escritura ---
    
    async def _record_history(self, answer: OperatorFieldAnswerModel) -> None:
        self._session.add(OperatorFieldAnswerHistoryModel(
            operator_field_answer_id=answer.id,
            value_text=answer.value_text,
            reference_id=answer.reference_id,
            validation_state=answer.validation_state,
            observations=answer.observations,
            evaluated_by=answer.evaluated_by,
            evaluated_at=answer.evaluated_at,
            recorded_at=datetime.now(timezone.utc),
        ))
        await self._session.flush()

    async def save_text_answer(self, operator_id: int, field_rule_id: int, value: str) -> Answer:
        model = await self._get_or_new_answer(operator_id, field_rule_id)
        model.value_text = value
        model.reference_id = None
        model.validation_state = "pending_verification"
        model.observations = None
        await self._session.flush()
        await self._record_history(model)
        return _answer_to_entity(model)

    async def save_file_answer(self, operator_id, field_rule_id, type_file_id, url, name) -> Answer:
        document = OperatorDocumentModel(
            operator_id=operator_id, type_file_id=type_file_id,
            url=url, name=name,
        )
        self._session.add(document)
        await self._session.flush()  
        
        print(f"Document: {document.__dict__}") 
        
        ref = ReferenceAnswerModel(file_id=document.id)
        self._session.add(ref)
        await self._session.flush()

        model = await self._get_or_new_answer(operator_id, field_rule_id)
        model.value_text = None
        model.reference_id = ref.id
        model.validation_state = "pending_verification"
        model.observations = None
        await self._session.flush()
        await self._record_history(model)
        return _answer_to_entity(model)

    async def save_address_answer(self, operator_id: int, field_rule_id: int, address_data: dict) -> Answer:
        address = OperatorAddressModel(operator_id=operator_id, **address_data)
        self._session.add(address)
        await self._session.flush()
        
        ref = ReferenceAnswerModel(address_id = address.id)
        self._session.add(ref)
        await self._session.flush()
        
        model = await self._get_or_new_answer(operator_id, field_rule_id)
        model.value_text = None
        model.reference_id = ref.id
        model.validation_state = "pending_verification"
        model.observations = None
        await self._session.flush()
        await self._record_history(model)
        return _answer_to_entity(model)
    
    
    async def save_catalog_reference_answer(self, operator_id: int, field_rule_id: int, catalog_column: int, catalog_id: int):
        ref = ReferenceAnswerModel(**{catalog_column: catalog_id})
        self._session.add(ref)
        await self._session.flush()
        
        model = await self._get_or_new_answer(operator_id, field_rule_id)
        model.value_text = None
        model.reference_id = ref.id
        model.validation_state = "pending_verification"
        model.observations = None
        await self._session.flush()
        await self._record_history(model)
        return _answer_to_entity(model)
    

    async def evaluate_answer(self, answer_id: int, validation_state: str, observations: str | None, evaluated_by: str | None) -> Answer:
        model = await self._session.get(OperatorFieldAnswerModel, answer_id)
        model.validation_state = validation_state
        model.observations = observations
        model.evaluated_by = evaluated_by
        model.evaluated_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._record_history(model)
        return _answer_to_entity(model)
    
    async def get_all_answers_for_operator(self, operator_id: int) -> list[Answer]:
        result = await self._session.execute(
            select(OperatorFieldAnswerModel).where(OperatorFieldAnswerModel.operator_id == operator_id)
        )
        return [_answer_to_entity(a) for a in result.scalars().all()]
    
    async def get_files_by_ids(self, ids: list[int]) -> dict[int, FileDetail]:
        if not ids:
            return {}
        result = await self._session.execute(select(OperatorDocumentModel).where(OperatorDocumentModel.id.in_(ids)))
        return {
            d.id: FileDetail(id=d.id, type_file_id=d.type_file_id, name=d.name, url=d.url)
            for d in result.scalars().all()
        }
        
    async def get_addresses_by_ids(self, ids: list[int]) -> dict[int, AddressDetail]:
        if not ids:
            return {}
        result = await self._session.execute(select(OperatorAddressModel).where(OperatorAddressModel).id.in_(ids))
        return {
            a.id: AddressDetail(
                id=a.id, address_type_id=a.address_type_id, street=a.street,
                ext_number = a.ext_number, int_number=a.int_number, neighborhood=a.neighborhood,
                city=a.city, state= a.state, zip_code=a.zip_code, country=a.country,
            )
            for a in result.scalars().all()
        }