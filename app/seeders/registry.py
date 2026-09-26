from app.seeders.base import Seeder

SEEDER_REGISTRY: dict[str,type[Seeder]] = {}

def register_seeder(cls: type[Seeder]) -> type[Seeder]:
    """Decorador: registra un seeder bajo su 'name' para poder invocarlo por ese nombre"""
    SEEDER_REGISTRY[cls.name] = cls
    return cls