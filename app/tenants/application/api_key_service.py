import secrets
import hashlib
from app.tenants.domain.repository import TenantRepository
from datetime import datetime, timezone
from app.core.logging import get_logger




class ApiKeyService:
    def __init__(self, tenant_repo: TenantRepository):
        self._repo = tenant_repo
        self._logger = get_logger("tenants_api_key")
        
    async def generate_api_key(
        self,
        tenant_id: str,
        domain:str,
        name: str | None = None,
        
    ) -> tuple[str, str]:
        
        #
        #Genera una API key, guarda su hash y prefijo en la DB.
        #Retorna la key en texto plano Solo una vez: (plain_key, key_prefix)
        #
        
        raw_key = f"sk_live_{secrets.token_urlsafe(32)}"
        
        key_prefix = raw_key[:12]
        
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        await self._repo.create_api_key_domain(
            tenant_id=tenant_id,
            domain=domain,
            key_prefix=key_prefix,
            key_hash=key_hash,
            name=name,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
       #Temporalmente almacenar en un log para posteriormente guardarlo en un vault o por email
       
        print("GUARDANDO LOG")
        print(raw_key, key_prefix)
        
        print("DEBUG disabled:", self._logger.disabled)
        print("DEBUG level:", self._logger.level)
        print("DEBUG handlers:", self._logger.handlers)
        print("DEBUG propagate:", self._logger.propagate)
        
        self._logger.info(
            f"Dominio: {domain} "
            f"| raw_key: {raw_key} "
            f"| key_prefix: {key_prefix} "
        )
        
        return {
            "raw_key": raw_key,
            "key_prefix": key_prefix
        }
        