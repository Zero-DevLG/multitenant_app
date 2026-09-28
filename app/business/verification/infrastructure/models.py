from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    case
)

from datetime import datetime, timezone
from app.core.database import BusinessBase as Base

class Modules(Base):
    __tablename__ = "modules"
    id=Column(Integer, primary_key=True)
    name=Column(Text, nullable=False)
    code=Column(Text, nullable=False)
    description=Column(Text, nullable=True)
    status_id=Column(Integer, nullable=False, default=1)
    required=Column(Boolean, default=True)
    
    
class Sections(Base):
    __tablename__ = "sections"
    id=Column(Integer, primary_key=True)
    name=Column(String(255), nullable=False)
    code=Column(String(255), nullable=False)
    description=Column(Text, nullable=True)
    status_id=Column(Integer, nullable=False, default=1)
    module_id=Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    required=Column(Boolean, default=True)

class SectionFieldRuleModel(Base):
    __tablename__ = "section_field_rules"
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    required = Column(Boolean, nullable=False, default=False)
    active=Column(Boolean, nullable=False, default=True)
    created_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    __table_args__=(UniqueConstraint("section_id", "code", name="uq_section_field_code"),)    
    
    
class SectionStatusRuleModel(Base):
    __tablename__="section_status_rules"
    id=Column(Integer,primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    priority = Column(Integer,nullable=False)
    condition_name = Column(String(100), nullable=False)
    result_status = Column(String(50), nullable=False)
    
class ModuleStatusRuleModel(Base):
    __tablename__ = "module_status_rules"
    id=Column(Integer,primary_key=True)
    module_id = Column(Integer,ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    priority = Column(Integer, nullable=False)
    condition_name = Column(String(100), nullable=False)
    result_status = Column(String(50), nullable=False)


class OperatorFieldAnswerModel(Base):
    __tablename__ = "operator_field_answers"
    id = Column(Integer, primary_key=True)
    operator_id =  Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False)
    section_field_rule_id = Column(Integer, ForeignKey("section_field_rules.id", ondelete="RESTRICT"), nullable=False)
    
    value_text = Column(Text, nullable=True)
    reference_id = Column(Integer, ForeignKey("reference_answers.id", ondelete="RESTRICT"), nullable=True)
   
    
    validation_state = Column(String(20), nullable=False, default="pending_verification")
    observations = Column(Text, nullable=True)
    evaluated_by = Column(String(100), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint("operator_id", "operator_id", "section_field_rule_id",name="uq_operator_field"),)
    
    

class OperatorFieldAnswerHistoryModel(Base):
    __tablename__= "operator_field_answer_history"
    id = Column(Integer,primary_key=True)
    
    operator_field_answer_id = Column(Integer, ForeignKey("operator_field_answers.id", ondelete="SET NULL"), nullable=True)
    value_text = Column(Text, nullable=True)
    reference_id = Column(Integer, ForeignKey("reference_answers.id", ondelete="RESTRICT"), nullable=True)
    
    validation_state = Column(String(20), nullable=False)
    observations = Column(Text, nullable=True)
    evaluated_by = Column(String(100), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    
    recorded_at = Column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc), nullable=False, index=True)
    

class ReferenceAnswerModel(Base):
    __tablename__ = "reference_answers"
    id = Column(Integer, primary_key=True)
    
    file_id = Column(Integer, ForeignKey("operators_files.id", ondelete="RESTRICT"), nullable=True)
    address_id = Column(Integer, ForeignKey("operators_addresses.id", ondelete="RESTRICT"), nullable=True)
    legal_authority_role_id = Column(Integer,ForeignKey("catalog_legal_title_authority_role.id", ondelete="RESTRICT"), nullable=True)
    entity_type_id = Column(Integer,ForeignKey("catalog_entity_type.id", ondelete="RESTRICT"), nullable=True)
    business_activity_id = Column(Integer, ForeignKey("catalog_business_activity.id", ondelete="RESTRICT"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint(
            case((file_id.isnot(None), 1), else_=0)
            + case((address_id.isnot(None),1), else_=0)
            + case((legal_authority_role_id.isnot(None),1), else_=0)
            + case((entity_type_id.isnot(None), 1), else_=0)
            + case((business_activity_id.isnot(None), 1), else_=0)
            == 1,
            name='ck_reference_answers_exactly_one'
        ),
    )


# CATALOGS
    
class LegalTitleAuthorityRole(Base):
    __tablename__ = "catalog_legal_title_authority_role"
    id = Column(Integer, primary_key=True)
    name=Column(String(100), nullable=False)
    description=Column(Text, nullable=True)
    active=Column(Boolean, default=True, nullable=False)
    

class Entitytype(Base):
    __tablename__ = "catalog_entity_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)

class BusinessActivity(Base):
    __tablename__ = "catalog_business_activity"
    id = Column(Integer,primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    

class SectionFieldFileTypeModel(Base):
    __tablename__="section_field_file_types"
    id=Column(Integer,primary_key=True)
    section_field_rule_id = Column(Integer, ForeignKey("section_field_rules.id", ondelete='CASCADE'), nullable=False, index=True)
    catalog_type_file_id = Column(Integer, ForeignKey("catalog_types_files.id", ondelete="RESTRICT"),nullable=False, index=True,)
    
    __table_args__ = (UniqueConstraint("section_field_rule_id", "catalog_type_file_id", name="uq_field_file_type"),)