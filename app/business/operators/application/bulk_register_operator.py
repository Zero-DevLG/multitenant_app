from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.exceptions import TenantNotFoundError, TenantNotActiveError
from app.tenants.infrastructure.tenant_resolver import tenant_resolver
from app.tenants.infrastructure.engine_factory import engine_factory
from app.business.operators.infrastructure.repository_sqlalchemy import SqlAlchemyOperatorRepository
from app.business.users.infrastructure.repository_sqlalchemy import SqlAlchemyUserRepository
from app.business.operators.infrastructure.repository_sqlalchemy import SqlAlchemyOperatorUserRepository
from app.business.operators.api.schemas import BulkOperatorRegisterRequest
from app.core.security import generate_temp_password, hash_password

from app.core.logging import get_logger

logger = get_logger("operators")

class BulkOperatorRegistrationService:
    
    def __init__(self, control_repo: TenantRepository):
        self._control_repo = control_repo
        
    async def register_in_tenants(self, operator_data: BulkOperatorRegisterRequest):
        
        results = []
        
        print("Accediendo")
        print(operator_data.domains)
        
        for domain in operator_data.domains:
            try:
                print(domain.trade_name) 
                print("Obteniendo tenant")       
                tenant = await tenant_resolver.resolve(domain.domain, self._control_repo)
              
                print(tenant)
                
            except (TenantNotFoundError, TenantNotActiveError) as e:
                logger.warning(f"Pre-registro omitido: domain={domain.trade_name} razón={e}")
                results.append({"domain": domain.trade_name, "status": "failed", "reason": str(e)})
                continue
            
            
            sessionmaker = await engine_factory.get_sessionmaker(tenant)
            async with sessionmaker() as session:
                repo = SqlAlchemyOperatorRepository(session)
                user_repo = SqlAlchemyUserRepository(session)
                operator_user_repo = SqlAlchemyOperatorUserRepository(session)
                
                existing = await repo.get_by_rfc(operator_data.operator.rfc_tax_id)
                if existing is not None:
                    logger.info(f"Operador ya existe en domain: {domain.domain} rfc:{operator_data.operator.rfc_tax_id}")
                    results.append({"domain": domain.domain, "status": "skipped", "reason": "Ya existe el operador registrado en el tenant"})
                    continue
                
                try:
                    mo_temp = f"{operator_data.operator.mo}-{tenant.prefix}-"
                    operator = await repo.create(operator_data, mo_temp)
                    temp_password = generate_temp_password()
                    user = await user_repo.create(
                        name=f"admin-{operator.trade_name}",
                        second_name="",
                        last_name=f"admin-{operator.trade_name}",
                        second_last_name="",
                        email=f"{operator.email}",
                        phone_wa=f"{operator.phone}",
                        status_id=1,
                        group_id=1,
                        password_hash=hash_password(temp_password)
                    )
                    
                    await operator_user_repo.link(operator.id, user.id)
                    
                    await session.commit()
                    
                    logger.info(f"Operador y usuario creados: domain={domain.domain} operator_id={operator.id} | USER: {user.id} PASS: {temp_password}")
                    
                    results.append({
                        "domain": domain.domain,
                        "status": "created",
                        "operator_id": operator.id,
                        "user_id": user.id,
                        "temp_password": temp_password,
                    })
                    
                    # Enviar información por correo posteriormente
                except Exception as e:
                    logger.error(f"Error creando operador domain:{domain.domain} error={e}")
                    results.append({"domain": domain.domain, "status": "failed", "reason": str(e)})
                        
                
                    
        return results