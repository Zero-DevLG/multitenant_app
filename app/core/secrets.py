import secrets as _secrets
import httpx
from app.core.config import settings

def generate_safe_password(long: int = 32) -> str:
    return _secrets.token_urlsafe(long)

async def save_secret(name: str, value: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.VAULT_URL}/v1/secret/data/{name}",
            headers={"X-Vault-Token": settings.VAULT_TOKEN},
            json={"data": {"password": value}},
        )
        resp.raise_for_status()
    return f"secret/data/{name}"

async def get_secret(secret_ref: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.VAULT_URL}/v1/{secret_ref}",
            headers={"X-Vault-Token": settings.VAULT_TOKEN},
        )
        resp.raise_for_status()
        return resp.json()["data"]["data"]["password"]