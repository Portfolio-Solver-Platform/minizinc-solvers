from typing import Callable, Awaitable
from psp_solver_sdk.queue import QueueMessageProcessor


def mock_process_loop(
    monkeypatch, inputs: list[bytes], output_check: Callable[[list[bytes]], None]
):
    async def new_process_loop(self, process: Callable[[bytes], Awaitable[bytes]]):
        outputs = []
        for input in inputs:
            outputs.append(await process(input))
        output_check(outputs)

    monkeypatch.setattr(QueueMessageProcessor, "process_loop", new_process_loop)
