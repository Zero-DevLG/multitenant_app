import asyncio
from app.core.redis_client import get_redis

async def test():
    r = get_redis()
    await r.set("test_key", "NXTEST", ex=30)
    value = await r.get("test_key")
    print("Valor leído:", value)
    
asyncio.run(test())