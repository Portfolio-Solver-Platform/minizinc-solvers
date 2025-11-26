from .config import QueueConfig, QueueAuthConfig
from typing import Callable, Awaitable
import aio_pika
import json

QueueConnection = aio_pika.abc.AbstractRobustConnection


async def get_connection(auth: QueueAuthConfig) -> QueueConnection:
    return await aio_pika.connect_robust(
        host=auth.host,
        port=auth.port,
        login=auth.user,
        password=auth.password,
    )


class QueueMessageProcessor:
    config: QueueConfig

    async def process_loop(self, process: Callable[[bytes], Awaitable[bytes]]):
        async with await get_connection(self.config.auth) as connection:
            channel = await connection.channel()
            in_queue = await channel.declare_queue(self.config.in_name, durable=True)
            await channel.declare_queue(self.config.out_name, durable=True)
            exchange = channel.default_exchange

            async with in_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        out_body = await process(message.body)
                        await exchange.publish(
                            aio_pika.Message(
                                body=out_body,
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key=self.config.out_name,
                        )

    async def json_process_loop(self, process: Callable[[dict], Awaitable[dict]]):
        async def process_bytes(input: bytes) -> bytes:
            in_data = json.loads(input.decode())
            out = await process(in_data)
            return json.dumps(out).encode()

        return await self.process_loop(process_bytes)
