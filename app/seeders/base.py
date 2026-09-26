from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

class Seeder(ABC):
    name:str # Identificador unico
    
    @abstractmethod
    async def run(self, session: AsyncSession) -> None:
        """Ejecuta la siembra de datos usando la sesion de una base de datos de tenant especifica"""
        ...