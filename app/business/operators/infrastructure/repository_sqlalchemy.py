from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.business.operators.domain.repository import OperatorRepository, OperatorUserRepository
from app.business.operators.domain.entities import Operator, OperatorUserLink
from app.business.operators.models.model import Operator as OperatorModel, OperatorUserModel
from app.business.operators.api.schemas import BulkOperatorRegisterRequest


def _to_entity(model: OperatorModel) -> Operator:
    return Operator(
        id=model.id, mo=model.mo, trade_name=model.trade_name, company_name=model.company_name,
        email=model.email, phone=model.phone, rfc_tax_id=model.rfc_tax_id
    )
    
class SqlAlchemyOperatorRepository(OperatorRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        

    async def get_by_rfc(self, rfc: str) -> Operator | None:
        result = await self._session.execute(select(OperatorModel).where(OperatorModel.rfc_tax_id == rfc))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None


    async def create(self, data: BulkOperatorRegisterRequest, mo_temp: str ) -> Operator:
        op_data =data.operator
        
        new_operator = OperatorModel(
            mo=mo_temp,
            operator_status_id=2,
            operator_type_id=op_data.operator_type_id,
            operator_class_id=op_data.operator_class_id,
            trade_name=op_data.trade_name,
            company_name=op_data.company_name,
            rfc_tax_id=op_data.rfc_tax_id,
            website=op_data.website,
            email_fiscal_contact=op_data.email_fiscal_name,
            cedula_fiscal_name=op_data.cedula_fiscal_name,
            email=op_data.email,
            contact_name=op_data.contact_name,
            code_alfa=op_data.code_alfa,
            code_num=op_data.code_num,
            phone=op_data.phone
        )
        
        self._session.add(new_operator)
        
        await self._session.flush()
        
        new_operator.mo = f"{mo_temp}{new_operator.id:04d}"
        
        #await self._session.commit()
        #await self._session.refresh(new_operator)
        
        return new_operator
    
class SqlAlchemyOperatorUserRepository(OperatorUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        
    
    async def link(self, operator_id: int, user_id:int) -> OperatorUserLink:
        model = OperatorUserModel(operator_id=operator_id, user_id=user_id)
        self._session.add(model)
        await self._session.flush()
        return OperatorUserLink(id=model.id, operator_id=model.operator_id, user_id=model.user_id)
    
    async def get_operator_by_user_id(self, user_id:int) -> Operator | None:
        result = await self._session.execute(
            select(OperatorModel).join(OperatorUserModel, OperatorUserModel.operator_id == OperatorModel.id).where(OperatorUserModel.user_id == user_id)
        )
        
        model = result.scalar_one_or_none()
        
        return _to_entity(model) if  model else None