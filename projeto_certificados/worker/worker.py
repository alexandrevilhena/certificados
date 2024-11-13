import aio_pika
import asyncio
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from database import get_db
from models import Certificado

async def process_message(message):
    try:
        certificado_id = int(message.body.decode())
        db: Session = next(get_db())
        certificado = db.query(Certificado).get(certificado_id)

        if not certificado:
            print(f"Certificado com ID {certificado_id} não encontrado.")
            await message.nack(requeue=False)
            return

        c = canvas.Canvas(f"certificados/{certificado_id}.pdf")
        c.drawString(100, 750, f"Nome: {certificado.nome}")
        c.drawString(100, 720, f"Curso: {certificado.curso}")
        c.drawString(100, 690, f"Data de Conclusão: {certificado.data_conclusao}")
        c.save()

        certificado.status = "CONCLUÍDO"
        db.commit()
        print(f"Certificado {certificado_id} processado com sucesso.")
        await message.ack()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        await message.nack(requeue=False)

async def connect_to_rabbitmq():
    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            print("Conectado ao RabbitMQ")
            return connection
        except aio_pika.exceptions.AMQPConnectionError as e:
            print(f"Falha ao conectar, tentativa {attempt + 1}: {e}")
            await asyncio.sleep(10)
    raise Exception("Não foi possível se conectar ao RabbitMQ após várias tentativas")

async def main(connection):
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("diploma_certificados", durable=True)
        print("Esperando mensagens...")

        await queue.consume(process_message)

        await asyncio.Future()

async def start():
    connection = await connect_to_rabbitmq()
    await main(connection)

if __name__ == "__main__":
    asyncio.run(start())
