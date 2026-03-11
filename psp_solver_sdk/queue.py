from .config import QueueConfig, QueueAuthConfig
from typing import Callable, Awaitable
from dataclasses import dataclass, field
import asyncio
import signal
import aio_pika
import json
import logging

logger = logging.getLogger(__name__)


async def get_connection(
    auth: QueueAuthConfig,
) -> aio_pika.abc.AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=auth.host,
        port=auth.port,
        login=auth.user,
        password=auth.password,
    )


@dataclass
class QueueMessageProcessor:
    config: QueueConfig
    _shutdown: asyncio.Event = field(default_factory=asyncio.Event, init=False)

    async def process_loop(self, process: Callable[[bytes], Awaitable[bytes]]):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGTERM, self._handle_sigterm)

        async with await get_connection(self.config.auth) as connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
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
                    if self._shutdown.is_set():
                        logger.info("Shutdown requested, exiting after completing current message.")
                        return

    async def json_process_loop(self, process: Callable[[dict], Awaitable[dict]]):
        async def process_bytes(input: bytes) -> bytes:
            in_data = json.loads(input.decode())
            out = await process(in_data)
            return json.dumps(out).encode()

        return await self.process_loop(process_bytes)

    def _handle_sigterm(self):
        logger.info("Received SIGTERM, will shut down after current message.")
        self._shutdown.set()
