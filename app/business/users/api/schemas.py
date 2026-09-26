from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name:str
    last_name:str
    email: EmailStr
    password: str
    phone_wa: str
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token:str
    token_type: str = "bearer"