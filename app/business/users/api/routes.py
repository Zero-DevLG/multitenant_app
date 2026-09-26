from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tenants.api.deps import get_tenant_db_session
from app.business.users.infrastructure.repository_sqlalchemy import SqlAlchemyUserRepository
from app.business.operators.infrastructure.repository_sqlalchemy import SqlAlchemyOperatorUserRepository
from app.business.users.application.register_user import RegisterUserService
from app.business.users.application.authenticate_user import AuthenticateUserService
from app.business.users.domain.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from .schemas import RegisterRequest, LoginRequest, TokenResponse
from app.business.users.models import User


router = APIRouter(prefix="/users")

@router.get("/")
async def list_users(session: AsyncSession = Depends(get_tenant_db_session)):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_tenant_db_session)):
    service = RegisterUserService(SqlAlchemyUserRepository(session))
    try:
        user = await service.register(data.name, data.last_name, data.email, data.password, data.phone_wa)
    except EmailAlreadyRegisteredError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"id": user.id, "email": user.email}

@router.post("/login", response_model=dict)
async def login(
    data: LoginRequest, 
    session: AsyncSession = Depends(get_tenant_db_session)):
    service = AuthenticateUserService(
        SqlAlchemyUserRepository(session),
        SqlAlchemyOperatorUserRepository(session)
        )
    try:
        data_auth = await service.login(data.email, data.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return data_auth