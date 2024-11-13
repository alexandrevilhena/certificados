import aioredis

async def publish_message(certificado_id):
    redis = await aioredis.from_url("redis://redis")
    await redis.lpush("redis_to_rabbit", certificado_id)
    print(f"Mensagem {certificado_id} adicionada ao Redis")

