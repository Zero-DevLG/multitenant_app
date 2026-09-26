from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.business.users.domain.repository import UserRepository
from app.business.users.domain.entities import User
from app.business.users.models import User as UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id, name=model.name, last_name=model.last_name,
        email=model.email, password_hash=model.password_hash,
        status_id=model.status_id, group_id=model.group_id,
    )
    
class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return  _to_entity(model) if model else None
    
    async def create(self, **datos) -> User:
        model = UserModel(**datos)
        self._session.add(model)
        await self._session.flush()
        #await self._session.commit()
        #await self._session.refresh(model)
        return _to_entity(model)
    
    async def get_user_by_id(self, user_id):
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None