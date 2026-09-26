# scripts/sync_verification_rules.py
import asyncio
import argparse
import yaml
from pathlib import Path
from app.core.database import get_control_db_session_standalone, control_engine
from app.tenants.infrastructure.repository_sqlalchemy import SqlAlchemyTenantRepository
from app.tenants.infrastructure.engine_factory import engine_factory
from app.tenants.domain.entities import TenantStatus
from app.business.verification.infrastructure.repository_sqlalchemy import SqlAlchemyVerificationRuleRepository
from app.business.verification.domain.conditions import CONDITION_REGISTRY
from app.core.logging import get_logger

logger = get_logger("verification_rules")


def load_yaml_file(path: Path) -> dict:
    print(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_status_rules(status_rules: list[dict], file_label: str) -> list[str]:
    errores = []
    for regla in status_rules:
        if "when" not in regla or "result" not in regla:
            errores.append(f"[{file_label}] cada regla necesita 'when' y 'result'")
            continue
        if regla["when"] not in CONDITION_REGISTRY:
            errores.append(
                f"[{file_label}] condición desconocida: '{regla['when']}'. "
                f"Disponibles: {list(CONDITION_REGISTRY.keys())}"
            )
    if not any(r.get("when") == "all_required_correct" for r in status_rules):
        errores.append(f"[{file_label}] advertencia: falta una regla para el caso 'todo correcto'")
    return errores


async def sync_section_file(repo, data: dict) -> None:
    #print(data)
    module = await repo.upsert_module(code=data["module"],name=data["module"], required=True)
    section = await repo.upsert_section(module_id=module.id, code=data["code"], name=data["section"], required=True)

    print(f"section: {section}")

    yaml_codes = set()
    for field in data.get("fields", []):
        print(f"field: {field["code"]}")
        await repo.upsert_field_rule(
            section_id=section.id, code=field["code"], type_=field["type"], required=field["required"],
        )
        
        yaml_codes.add(field["code"])

    # Campos que ya no están en el YAML: se desactivan, nunca se borran
    for existing_field in await repo.get_field_rules(section.id):
        if existing_field.code not in yaml_codes:
            await repo.deactivate_field_rule(existing_field.id)
            logger.info(f"Campo desactivado: section={data['section']} code={existing_field.code}")

    await repo.replace_section_status_rules(section.id, data["status_rules"])


async def sync_module_file(repo, data: dict) -> None:
    module = await repo.upsert_module(code=data["code"],name=data["module"], required=True)
    print(module)
    await repo.replace_module_status_rules(module.id, data["status_rules"])


async def main(files: list[Path], domains: list[str] | None):
    # --- 1. Validar TODOS los archivos antes de tocar cualquier base de datos ---
    parsed_files = []
    for path in files:
        data = load_yaml_file(path)
        errores = validate_status_rules(data.get("status_rules", []), path.name)
        if errores:
            for e in errores:
                print(f"ERROR DE VALIDACIÓN: {e}")
            print(f"Se cancela toda la sincronización por errores en {path.name}")
            return
        parsed_files.append(data)

    # --- 2. Resolver a qué tenants aplica ---
    async with get_control_db_session_standalone() as control_session:
        tenant_repo = SqlAlchemyTenantRepository(control_session)
        if domains:
            tenants = []
            for domain in domains:
                tenant = await tenant_repo.get_by_domain(domain)
                if tenant is None:
                    print(f"AVISO: no existe un tenant con dominio '{domain}', se omite")
                    continue
                tenants.append(tenant)
        else:
            tenants = await tenant_repo.list_by_status(TenantStatus.ACTIVE)

    # --- 3. Aplicar, tenant por tenant, TODOS los archivos juntos en una sola transacción ---
    for tenant in tenants:
        try:
            sessionmaker = await engine_factory.get_sessionmaker(tenant)
            async with sessionmaker() as session:
                repo = SqlAlchemyVerificationRuleRepository(session)
                for data in parsed_files:
                    if "section" in data:
                        await sync_section_file(repo, data)
                    else:
                        await sync_module_file(repo, data)
                await session.commit()
            print(f"OK: {tenant.domain}")
            logger.info(f"Sincronización OK: domain={tenant.domain}")
        except Exception as e:
            print(f"FALLÓ: {tenant.domain} -> {e}")
            logger.error(f"Sincronización FALLÓ: domain={tenant.domain} error={e}")

    await control_engine.dispose()
    await engine_factory.dispose_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincroniza reglas de verificación (módulos/secciones) desde YAML")
    parser.add_argument("--files", required=True, help="Rutas de archivos YAML, separadas por coma")
    parser.add_argument("--domains", help="Dominios separados por coma. Si se omite, corre en TODOS los tenants activos")
    args = parser.parse_args()

    urls = [Path(f.strip()) for f in args.files.split(",")]
    domains = args.domains.split(",") if args.domains else None
    asyncio.run(main(urls, domains))