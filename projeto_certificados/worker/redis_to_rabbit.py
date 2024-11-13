import aioredis
import aio_pika
import asyncio
from aio_pika.exceptions import AMQPConnectionError
from aioredis.exceptions import RedisError

async def wait_for_service(url, retries=10, delay=5):
    """Função para aguardar um serviço estar disponível."""
    for attempt in range(retries):
        try:
            if "amqp" in url:
                connection = await aio_pika.connect_robust(url)
                await connection.close()
            elif "redis" in url:
                redis = await aioredis.from_url(url)
                await redis.ping()
                await redis.close()
            print(f"Conectado ao serviço em {url}")
            return
        except (AMQPConnectionError, RedisError):
            print(f"Tentativa {attempt + 1}/{retries}: Serviço em {url} não disponível, tentando novamente em {delay}s...")
            await asyncio.sleep(delay)
    raise ConnectionError(f"Não foi possível conectar ao serviço em {url} após {retries} tentativas.")

async def transfer_from_redis_to_rabbit():
    await wait_for_service("redis://redis")
    await wait_for_service("amqp://guest:guest@rabbitmq/")

    redis = await aioredis.from_url("redis://redis")
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")

    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("diploma_certificados", durable=True)

        while True:
            certificado_id = await redis.rpop("redis_to_rabbit")
            if certificado_id:
                await channel.default_exchange.publish(
                    aio_pika.Message(body=str(certificado_id).encode()),
                    routing_key="diploma_certificados",
                )
                print(f"Mensagem {certificado_id.decode()} enviada para RabbitMQ")
            else:
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(transfer_from_redis_to_rabbit())
