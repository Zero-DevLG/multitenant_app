from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.seeders.base import Seeder
from app.seeders.registry import register_seeder
from app.business.operators.models.model import OperatorsStatuses, OperatorType, OperatorsClass, OperatorsFiles, CatalogTypeFiles
from app.business.users.models import Groups,CatalogUserStatuses
from app.business.verification.infrastructure.models import Modules, Sections, LegalTitleAuthorityRole, Entitytype, BusinessActivity


@register_seeder
class DefaultCatalogsSeeder(Seeder):
    name = "default_catalogs"
    
    async def run(self, session: AsyncSession) -> None:
        await self._get_or_create(session, Groups, name="Sin asignar")
        await self._get_or_create(session, CatalogUserStatuses, name="activo", description="Usuario activo")
        await self._get_or_create(session, CatalogUserStatuses, name="pendiente_verificación", description="Correo aún no verificado")
        await self._get_or_create(session, CatalogUserStatuses, name="inactivo", description="Usuario inactivo")
        
        await self._get_or_create(session, OperatorsStatuses, name="pre_registro", description="Operador pre registrado")
        await self._get_or_create(session, OperatorsStatuses, name="registrado", description="Operador registrado")
        await self._get_or_create(session, OperatorsStatuses, name="inactivo", description="Operador inactivo")
        
        await self._get_or_create(session, OperatorType, name="Aéreo", description="Aéreo",key="A")
        await self._get_or_create(session, OperatorType, name="Terrestre", description="Terrestre",key="T")
        await self._get_or_create(session, OperatorType, name="Naviera", description="Naviera",key="N")
        await self._get_or_create(session, OperatorType, name="Visas", description="Visas",key="V")
        await self._get_or_create(session, OperatorType, name="Paquetería", description="Paquetería",key="P")
        await self._get_or_create(session, OperatorType, name="Compras Varias", description="Compras Varias",key="O")
        await self._get_or_create(session, OperatorType, name="Viáticos", description="Viáticos",key="D")
        await self._get_or_create(session, OperatorType, name="Reembolsos", description="Reembolsos",key="R")
        
        await self._get_or_create(session, OperatorsClass, name="Nacional", description="Nacional")
        await self._get_or_create(session, OperatorsClass, name="Internacional", description="Internacional")
        
        # CATALOG ENTITY_TYPE
        await self._get_or_create(session, Entitytype, id=1, name="Individual", description="")
        await self._get_or_create(session, Entitytype, id=2, name="Corporation", description="")
        
        # CATALOG BUSINESS_ACTIVITY
        await self._get_or_create(session, BusinessActivity, id=1, name="Agriculture, Forestry, Fishing and Hunting", description="")
        await self._get_or_create(session, BusinessActivity, id=2, name="Mining, Quarrying, and Oil and Gas Extraction", description="")
        await self._get_or_create(session, BusinessActivity, id=3, name="Utilities (Electricity, Gas, Water, Waste)", description="")
        await self._get_or_create(session, BusinessActivity, id=4, name="Construction", description="")
        await self._get_or_create(session, BusinessActivity, id=5, name="Manufacturing", description="")
        await self._get_or_create(session, BusinessActivity, id=6, name="Wholesale Trade", description="")
        await self._get_or_create(session, BusinessActivity, id=7, name="Retail Trade", description="")
        await self._get_or_create(session, BusinessActivity, id=8, name="Transportation and Warehousing", description="")
        await self._get_or_create(session, BusinessActivity, id=9, name="Information, Media and Telecommunications", description="")
        await self._get_or_create(session, BusinessActivity, id=10, name="Finance and Insurance", description="")
        await self._get_or_create(session, BusinessActivity, id=11, name="Real Estate, Rental and Leasing", description="")
        await self._get_or_create(session, BusinessActivity, id=12, name="Professional, Scientific, and Technical Services", description="")
        await self._get_or_create(session, BusinessActivity, id=13, name="Management of Companies / Administrative and Support", description="")
        await self._get_or_create(session, BusinessActivity, id=14, name="Educational Services", description="")
        await self._get_or_create(session, BusinessActivity, id=15, name="Health Care and Social Assistance", description="")
        await self._get_or_create(session, BusinessActivity, id=16, name="Arts, Entertainment, and Recreation", description="")
        await self._get_or_create(session, BusinessActivity, id=17, name="Accommodation and Food Services", description="")
        await self._get_or_create(session, BusinessActivity, id=18, name="Public Administration and Defense", description="")
        await self._get_or_create(session, BusinessActivity, id=19, name="Other Services / Not Listed", description="")
                
        # TYPE FILES CATALOG
        # Tax Certification / Official Tax Registration
        await self._get_or_create(session, CatalogTypeFiles, name="Tax Certification / Official Tax Registration", description="Tax Certification / Official Tax Registration", key="TXC")

        # Articles of Incorporation / Original Corporate Bylaws
        await self._get_or_create(session, CatalogTypeFiles, name="Articles of Incorporation / Original Corporate Bylaws", description="Articles of Incorporation / Original Corporate Bylaws", key="AOI")

        # Latest Bylaws Amendment / Corporate Amendment
        await self._get_or_create(session, CatalogTypeFiles, name="Latest Bylaws Amendment / Corporate Amendment", description="Latest Bylaws Amendment / Corporate Amendment", key="LBA")

        # Tax Registration Certificate
        await self._get_or_create(session, CatalogTypeFiles, name="Tax Registration Certificate", description="Tax Registration Certificate", key="TRC")

        # Tax Address Proof
        await self._get_or_create(session, CatalogTypeFiles, name="Tax Address Proof", description="Tax Address Proof", key="TAP")

        # Passport or Government IDF
        await self._get_or_create(session, CatalogTypeFiles, name="Passport or Government IDF", description="Passport or Government IDF", key="PID")

        # Personal Tax Registration Certificate / TIN Document
        await self._get_or_create(session, CatalogTypeFiles, name="Personal Tax Registration Certificate / TIN Document", description="Personal Tax Registration Certificate / TIN Document", key="PTR")

        # Power of Attorney / Certificate of Incumbency
        await self._get_or_create(session, CatalogTypeFiles, name="Power of Attorney / Certificate of Incumbency", description="Power of Attorney / Certificate of Incumbency", key="POA")

        # Cap Table or Ownership Structure
        await self._get_or_create(session, CatalogTypeFiles, name="Cap Table or Ownership Structure", description="Cap Table or Ownership Structure", key="CAP")

        # Certificate of Incumbency/Power of Attorney/Articles of Organization
        await self._get_or_create(session, CatalogTypeFiles, name="Certificate of Incumbency/Power of Attorney/Articles of Organization", description="Certificate of Incumbency/Power of Attorney/Articles of Organization", key="COI")

        # Trademark Registration Certificate
        await self._get_or_create(session, CatalogTypeFiles, name="Trademark Registration Certificate", description="Trademark Registration Certificate", key="TMC")

        # High Resolution Logo
        await self._get_or_create(session, CatalogTypeFiles, name="High Resolution Logo", description="High Resolution Logo", key="HRL")

        # Tourism License
        await self._get_or_create(session, CatalogTypeFiles, name="Tourism License", description="Tourism License", key="TLN")

        # Business Address Proof
        await self._get_or_create(session, CatalogTypeFiles, name="Business Address Proof", description="Business Address Proof", key="BAP")

        # Account Holder Name
        await self._get_or_create(session, CatalogTypeFiles, name="Account Holder Name", description="Account Holder Name", key="AHN")

        # Bank Letter / Certificate of Ownership
        await self._get_or_create(session, CatalogTypeFiles, name="Bank Letter / Certificate of Ownership", description="Bank Letter / Certificate of Ownership", key="BLC")
        
        # CATALOG LEGAL_TITLE_AUTHORITY_ROLE
        await self._get_or_create(session, LegalTitleAuthorityRole, id=1, name="director", description="", active=True)
        
        await self._get_or_create(session, LegalTitleAuthorityRole, id=2, name="board_member", description="", active=True)
        
        await self._get_or_create(session, LegalTitleAuthorityRole, id=3, name="president", description="", active=True)
        
        await self._get_or_create(session, LegalTitleAuthorityRole, id=4, name="vice_president", description="", active=True)
        
        await self._get_or_create(session, LegalTitleAuthorityRole, id=5, name="ceo", description="", active=True)
        
        await self._get_or_create(session, LegalTitleAuthorityRole, id=6, name="authorized_signatory", description="", active=True)
        
        
        # Catalog Modules
        await self._get_or_create(session, Modules, id=1, name="Legal Information", description="", status_id=1, required=True, code="legal_information")
        
        await self._get_or_create(session, Modules, id=2, name="Legal Representation", description="", status_id=1, required=True, code="legal_representation")
        
        await self._get_or_create(session, Modules, id=3, name="Ultimate Beneficial Owners & Shareholding", description="", status_id=1, required=True, code="ultimate_beneficial_owners_shareholding")
        
        await self._get_or_create(session, Modules,id=4, name="Business Information", description="", status_id=1, required=True, code="business_information")
        
        await self._get_or_create(session, Modules,id=5, name="Key Officers & Management", description="", status_id=1, required=True, code="key_officers_management")
        
        await self._get_or_create(session, Modules,id=6, name="Bank Accounts", description="", status_id=1, required=True, code="bank_accounts")
      
        await session.commit()
    
    
    
    @staticmethod
    async def _get_or_create(session: AsyncSession, model, **fields):
        result = await session.execute(select(model).where(model.name == fields["name"]))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        instance = model(**fields)
        session.add(instance)
        await session.flush()
        return instance