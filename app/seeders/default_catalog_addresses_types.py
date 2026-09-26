from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.seeders.base import Seeder
from app.seeders.registry import register_seeder
from app.business.operators.models.model import CatalogAddressTypeModel


@register_seeder
class DefaultAddressesType(Seeder):
    name = "default_catalog_addresses_type"
    
    async def run(self, session: AsyncSession) -> None:
        await self._get_or_create(session, CatalogAddressTypeModel, name="fiscal",description="fiscal" )