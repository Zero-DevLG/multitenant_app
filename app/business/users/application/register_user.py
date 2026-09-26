from app.business.users.domain.repository import UserRepository
from app.business.users.domain.exceptions import EmailAlreadyRegisteredError
from app.core.security import hash_password




class RegisterUserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo
        
    
    async def register(
        self,
        name:str,
        last_name: str,
        email: str,
        password: str,
        phone_wa: str,
    ):
        existing = await self._repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(f"El correo: {email} ya está registrado")
        
        return await self._repo.create(
            name=name,
            last_name=last_name,
            second_last_name="",
            email=email,
            password_hash=hash_password(password),
            phone_wa=phone_wa,
            status_id=1,
            group_id=None,
        )