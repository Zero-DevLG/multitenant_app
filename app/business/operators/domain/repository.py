from abc import ABC, abstractmethod
from .entities import Operator, OperatorUserLink, OperatorsFiles

class OperatorRepository(ABC):
    
    @abstractmethod
    async def get_by_rfc(self, rfc: str) -> Operator | None: ...
    
    
    @abstractmethod
    async def create(self, **data) -> Operator: ...
    
class OperatorUserRepository(ABC):
    @abstractmethod
    async def link(self, operator_id:int, user_id:int) -> OperatorUserLink: ...
    
    @abstractmethod
    async def get_operator_by_user_id(self,user_id:int) -> Operator | None: ... 
    
    
    
class OperatorsFiles(ABC):
    
    @abstractmethod
    async def create_operator_file(self, operator_id: int, type_file_id: int, name: str, url: str) -> OperatorsFiles: ...
    
    @abstractmethod
    async def get_files_by_id(self, operator_id: int) -> list[OperatorsFiles]: ...