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
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_status_rules(status_rules: list[dict], label: str) -> list[str]:
    errores = []
    for regla in status_rules:
        if "when" not in regla or "result" not in regla:
            errores.append(f"[{label}] cada regla necesita 'when' y 'result'")
            continue
        if regla["when"] not in CONDITION_REGISTRY:
            errores.append(f"[{label}] condición desconocida: '{regla['when']}'. Disponibles: {list(CONDITION_REGISTRY.keys())}")
    if not any(r.get("when") == "all_required_correct" for r in status_rules):
        errores.append(f"[{label}] falta una regla para el caso 'todo correcto'")
    return errores


def validate_document(data: dict) -> list[str]:
    """Recorre TODO el árbol (módulos → secciones → campos) antes de tocar cualquier base de datos."""
    errores = []
    for module_data in data.get("modules", []):
        module_name = module_data.get("name", "<sin nombre>")
        errores += validate_status_rules(module_data.get("status_rules", []), f"módulo '{module_name}'")

        for section_data in module_data.get("sections", []):
            section_name = section_data.get("name", "<sin nombre>")
            label = f"módulo '{module_name}' / sección '{section_name}'"
            errores += validate_status_rules(section_data.get("status_rules", []), label)

            codes_seen = set()
            for field in section_data.get("fields", []):
                code = field.get("code")
                if code in codes_seen:
                    errores.append(f"[{label}] código de campo repetido: '{code}'")
                codes_seen.add(code)

    return errores


async def sync_module(repo, module_data: dict) -> None:
    module = await repo.upsert_module(name=module_data["name"], code=module_data["code"], required=True)
    await repo.replace_module_status_rules(module.id, module_data["status_rules"])

    for section_data in module_data.get("sections", []):
        section = await repo.upsert_section(module_id=module.id, name=section_data["name"], code=section_data["code"], required=section_data.get("required", True))

        yaml_codes = set()
        for field in section_data.get("fields", []):
            field_rule = await repo.upsert_field_rule(
                section_id=section.id, code=field["code"], type_=field["type"], required=field["required"],
            )
            yaml_codes.add(field["code"])
            
            if field["type"] == "file" and "file_types" in field:
                catalog_ids = []
                for key in field["file_types"]:
                    catalog_id = await repo.get_catalog_type_file_by_key(key)
                    if catalog_id is None:
                        raise ValueError(f"El catalogo de archivos no tiene ninguna entrada con key: {key} en este tenant")
                    catalog_ids.append(catalog_id)
                await repo.replace_field_file_types(field_rule.id, catalog_ids)

        for existing_field in await repo.get_field_rules(section.id):
            if existing_field.code not in yaml_codes:
                await repo.deactivate_field_rule(existing_field.id)
                logger.info(f"Campo desactivado: section={section_data['name']} code={existing_field.code}")

        await repo.replace_section_status_rules(section.id, section_data["status_rules"])


async def main(file_path: Path, domains: list[str] | None):
    data = load_yaml_file(file_path)

    errores = validate_document(data)
    if errores:
        for e in errores:
            print(f"ERROR DE VALIDACIÓN: {e}")
        print("Se cancela la sincronización por errores en el archivo")
        return

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

    for tenant in tenants:
        try:
            sessionmaker = await engine_factory.get_sessionmaker(tenant)
            async with sessionmaker() as session:
                repo = SqlAlchemyVerificationRuleRepository(session)
                for module_data in data.get("modules", []):
                    await sync_module(repo, module_data)
                await session.commit()   # TODOS los módulos del archivo, para este tenant: todo o nada
            print(f"OK: {tenant.domain}")
            logger.info(f"Sincronización OK: domain={tenant.domain}")
        except Exception as e:
            print(f"FALLÓ: {tenant.domain} -> {e}")
            logger.error(f"Sincronización FALLÓ: domain={tenant.domain} error={e}")

    await control_engine.dispose()
    await engine_factory.dispose_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincroniza TODAS las reglas de verificación desde un solo archivo YAML")
    parser.add_argument("--file", required=True, help="Ruta al archivo YAML único con todos los módulos/secciones")
    parser.add_argument("--domains", help="Dominios separados por coma. Si se omite, corre en TODOS los tenants activos")
    args = parser.parse_args()

    domains = args.domains.split(",") if args.domains else None
    asyncio.run(main(Path(args.file), domains))