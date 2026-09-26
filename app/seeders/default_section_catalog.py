from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.seeders.base import Seeder
from app.seeders.registry import register_seeder
from app.business.verification.infrastructure.models import Sections

@register_seeder
class DefaultSectionSeeder(Seeder):
    name="default_section_catalog"
    
    async def run(self, session: AsyncSession) -> None:
        
        # 1
        await self._get_or_create(session, Sections, id=1, name="Legal Corporate Name", description="", status_id=1,module_id=1, required=True, code="legal_corporate_name")
        
        await self._get_or_create(session, Sections, id=2, name="Entity Type", description="", status_id=1,module_id=1, required=True, code="entity_type")
        
        await self._get_or_create(session, Sections, id=3, name="Articles of Incorporation (Original)", description="", status_id=1,module_id=1, required=True, code="articles_incorporation")
        
        await self._get_or_create(session, Sections, id=4, name="Bylaws Amendments (Latest)", description="", status_id=1,module_id=1, required=True, code="bylaws_amendments")
        
        await self._get_or_create(session, Sections, id=5, name="Tax Identification Number (Tax ID)", description="", status_id=1,module_id=1, required=True, code="tax_identification_number")
        
        await self._get_or_create(session, Sections, id=6, name="Standard Industrial Classification / Business Activity (NAICS/ISIC)", description="", status_id=1,module_id=1, required=True, code="standard_industrial_classification")
        
        await self._get_or_create(session, Sections, id=7, name="Registered Business Address", description="", status_id=1,module_id=1, required=True, code="registered_business_address")
        
        # 2
        await self._get_or_create(session, Sections, id=8, name="Legal Representative Full Name", description="", status_id=1,module_id=2, required=True, code="legal_representative_full_name")
        
        await self._get_or_create(session, Sections, id=9, name="Passport", description="", status_id=1,module_id=2, required=True, code="passport")
        
        await self._get_or_create(session, Sections, id=10, name="Representative Tax Identification Number (Tax ID)", description="", status_id=1,module_id=2, required=True, code="representative_tax_identification_number")
        
        await self._get_or_create(session, Sections, id=11, name="Legal Title / Authority Role", description="", status_id=2,module_id=2, required=True, code="legal_title_authority_role")
        
        await self._get_or_create(session, Sections, id=12, name="Official Representative Contact Email", description="", status_id=1,module_id=2, required=True, code="official_representative_contact_email")
        
        # 3
        await self._get_or_create(session, Sections, id=13, name="add_ultimate_beneficial_owners_&_shareholding", description="", status_id=1, module_id=3, required=True )
        
        # 4 
        await self._get_or_create(session, Sections, id=14, name="trade_brand_name", description="", status_id=1, module_id=4, required=True )
        
        await self._get_or_create(session, Sections, id=15, name="official_brand_logo", description="", status_id=1, module_id=4, required=True )
        
        await self._get_or_create(session, Sections, id=16, name="local_tourism_board_license_certificate", description="", status_id=1, module_id=4, required=True )
        
        await self._get_or_create(session, Sections, id=17, name="business_address", description="", status_id=1, module_id=4, required=True )
        
        
        
        
        
        
        await session.commit()

    
    
    @staticmethod
    async def _get_or_create(session: AsyncSession, model, **fields):
        result = await session.execute(select(model).where(model.name == fields["name"]))
        existing =result.scalar_one_or_none()
            
        if existing is None:
            session.add(model(**fields))