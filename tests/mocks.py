from typing import Callable, Awaitable
from psp_solver_sdk.queue import QueueMessageProcessor


def mock_process_loop(monkeypatch, inputs: list[bytes]):
    async def new_process_loop(self, process: Callable[[bytes], Awaitable[bytes]]):
        for input in inputs:
            await process(input)

    monkeypatch.setattr(QueueMessageProcessor, "process_loop", new_process_loop)
