from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.secrets import save_secret, generate_safe_password
from app.tenants.domain.repository import TenantRepository
from app.tenants.domain.entities import Tenant, TenantStatus

async def create_database(tenant: Tenant, repo: TenantRepository):
    print("Recibiendo Tenant")
    print(tenant)
    admin_engine = create_engine(settings.ADMIN_DSN, isolation_level="AUTOCOMMIT")
    password = generate_safe_password()
    user = f"{tenant.db_name}_user"
    
    with admin_engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{tenant.db_name}`"
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ))
        
        for host in ['%', 'localhost']:
            
            conn.execute(
                text(f"CREATE USER IF NOT EXISTS `{user}`@'{host}' IDENTIFIED BY  :pwd"),
                {"pwd": password},
            )
            
            conn.execute(
                text(f"ALTER USER `{user}`@'{host}' IDENTIFIED BY :pwd"),
                {"pwd": password},
            )
        #conn.execute(
            #text(f"GRANT ALL PRIVILEGES ON `{tenant.db_name}`.* TO '{user}'@'%'"))
        
            conn.execute(text(f"GRANT ALL PRIVILEGES ON `{tenant.db_name}`.* TO `{user}`@'{host}'"))
            
            conn.execute(text("FLUSH PRIVILEGES"))
        
    secret_ref = await save_secret(tenant.db_name, password)
    await repo.update_status(tenant.id, TenantStatus.PROVISIONING_DB_DONE)
    return secret_ref