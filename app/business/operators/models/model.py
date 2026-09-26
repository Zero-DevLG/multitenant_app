from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint
)

from datetime import datetime, timezone
from app.core.database import BusinessBase as Base

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True)
    mo = Column(String(50))
    operator_status_id = Column(Integer, ForeignKey("catalog_operators_statuses.id"), index=True)
    operator_type_id = Column(Integer, ForeignKey("catalog_operators_type.id"), index=True)
    operator_class_id = Column(Integer, ForeignKey("catalog_operators_class.id"), index=True)
    trade_name = Column(String(100), nullable=True)
    company_name = Column(String(100), nullable=True)
    rfc_tax_id = Column(String(20))
    website = Column(String(100), nullable=True),
    email_fiscal_contact = Column(String(100), nullable=True)
    cedula_fiscal_name = Column(String(100), nullable=True)
    contact_name = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(15))
    code_num = Column(String(45), nullable=True)
    code_alfa = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=True)
        
        

class OperatorType(Base):
    __tablename__ = "catalog_operators_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    key = Column(String(5), nullable=False)
   

        
class OperatorsClass(Base):
    __tablename__ = "catalog_operators_class"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    key = Column(String(5), nullable=True)
  

class OperatorsStatuses(Base):
    __tablename__ = "catalog_operators_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
  

class OperatorUserModel(Base):
    __tablename__ = "operators_users"
    id=Column(Integer, primary_key=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at=Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc), nullable=True)
    
    __table_args__ = (UniqueConstraint("user_id", name="uq_operators_users_user_id"),)
    
    
class OperatorsFiles(Base):
    __tablename__= "operators_files"
    id=Column(Integer, primary_key=True)
    operator_id=Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    type_file_id=Column(Integer,ForeignKey("catalog_types_files.id", ondelete="CASCADE"), nullable=False, index=True)
    name=Column(String(255), nullable=False)
    url=Column(String(255), nullable=False)
    created_at=Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc), nullable=True)
    
class CatalogTypeFiles(Base):
    __tablename__ = "catalog_types_files"
    id=Column(Integer,primary_key=True)
    name=Column(String(255),nullable=False)
    description=Column(Text, nullable=False)
    key=Column(String(5), nullable=False)
    

class CatalogAddressTypeModel(Base):
    __tablename__ = "catalog_addresses_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
class OperatorAddressModel(Base):
    __tablename__ = "operators_addresses"
    id = Column(Integer, primary_key=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type_id = Column(Integer, ForeignKey("catalog_addresses_types.id"), nullable=False, index=True)
    street = Column(String(255), nullable=False)
    ext_number = Column(String(20), nullable=False)
    int_number = Column(String(20), nullable=False)
    neighborhood = Column(String(150), nullable=True)
    city = Column(String(150), nullable=False)
    state = Column(String(150), nullable=False)
    zip_code = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False)
    
    
    