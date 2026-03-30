from .config import QueueConfig, QueueAuthConfig
from typing import Callable, Awaitable
from dataclasses import dataclass, field
import asyncio
import signal
import aio_pika
import json
import logging

logger = logging.getLogger(__name__)


RETRY_DELAYS = [5, 30, 60]


async def retry_or_dlq(channel, queue_name: str, message: aio_pika.abc.AbstractIncomingMessage, exc: Exception):
    attempt = int((message.headers or {}).get("x-attempt", 0))
    headers = {**dict(message.headers or {}), "x-attempt": attempt + 1}

    if attempt < len(RETRY_DELAYS):
        delay = RETRY_DELAYS[attempt]
        routing_key = f"{queue_name}.retry.{delay}s"
        logger.warning(f"Retrying message (attempt {attempt + 1}/{len(RETRY_DELAYS)}, delay {delay}s): {exc}")
    else:
        routing_key = f"{queue_name}.dlq"
        logger.error(f"Message failed after {len(RETRY_DELAYS)} attempts, routing to DLQ: {exc}")

    try:
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.body,
                headers=headers,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        await message.ack()
    except Exception:
        logger.exception("Failed to publish to retry/DLQ, requeueing original message")
        await message.nack(requeue=True)


async def declare_quorum_queue(channel, name: str, consumer_timeout_s: int | None = None) -> aio_pika.abc.AbstractQueue:
    arguments = {"x-queue-type": "quorum"}
    if consumer_timeout_s is not None:
        arguments["x-consumer-timeout"] = (consumer_timeout_s + 60) * 1000
    queue = await channel.declare_queue(name, durable=True, arguments=arguments)
    for delay in [5, 30, 60]:
        await channel.declare_queue(
            f"{name}.retry.{delay}s",
            durable=True,
            arguments={
                "x-queue-type": "quorum",
                "x-message-ttl": delay * 1000,
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": name,
            },
        )
    await channel.declare_queue(f"{name}.dlq", durable=True, arguments={"x-queue-type": "quorum"})
    return queue


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
            in_queue = await declare_quorum_queue(channel, self.config.in_name, self.config.consumer_timeout)
            await channel.declare_queue(self.config.out_name, durable=True, arguments={"x-queue-type": "quorum"})
            exchange = channel.default_exchange

            async with in_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        out_body = await process(message.body)
                        await exchange.publish(
                            aio_pika.Message(
                                body=out_body,
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            ),
                            routing_key=self.config.out_name,
                        )
                        await message.ack()
                    except Exception as e:
                        await retry_or_dlq(channel, self.config.in_name, message, e)
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
