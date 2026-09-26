from app.business.users.domain.repository import UserRepository
from app.business.operators.domain.repository import OperatorUserRepository
from app.business.users.domain.exceptions import InvalidCredentialsError
from app.core.security import verify_password, create_access_token

class AuthenticateUserService:
    def __init__(self, 
                 repo: UserRepository, 
                 operator_user_repo: OperatorUserRepository
                 ):
        self._repo = repo
        self._operator_user_repo = operator_user_repo
        
    async def login(self, email:str, password: str) -> dict:
        user = await self._repo.get_by_email(email)
        print(user)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Credenciales Inválidas")
        
        operator = await self._operator_user_repo.get_operator_by_user_id(user.id)
        if operator is None:
            raise InvalidCredentialsError("Usuario sin operador")
        
        token = create_access_token(user_id=user.id, email=user.email)
        
        return {
            "name": f"{user.name} {user.last_name}",
            "email": email,
            "token": token,
            "operator": operator
        }