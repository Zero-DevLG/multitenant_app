# app/business/users/api/deps.py
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenants.api.deps import get_tenant_db_session
from app.business.users.infrastructure.repository_sqlalchemy import SqlAlchemyUserRepository
from app.business.operators.infrastructure.repository_sqlalchemy import SqlAlchemyOperatorUserRepository
from app.business.operators.domain.entities import Operator
from app.core.security import decode_access_token


async def get_current_user_and_operator(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_tenant_db_session),
) -> Operator:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante o con formato incorrecto")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_repo = SqlAlchemyUserRepository(session)
    user = await user_repo.get_user_by_id(int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail="El usuario del token ya no existe")

    operator_user_repo = SqlAlchemyOperatorUserRepository(session)
    operator = await operator_user_repo.get_operator_by_user_id(user.id)
    if operator is None:
        raise HTTPException(status_code=403, detail="Este usuario no representa a ningún operador")

    return operator