from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ADMIN_DSN: str
    CONTROL_DB_DSN: str
    DB_HOST: str
    DB_PORT: int = 5432
    VAULT_URL: str
    VAULT_TOKEN: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # REDIS
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        
settings = Settings()