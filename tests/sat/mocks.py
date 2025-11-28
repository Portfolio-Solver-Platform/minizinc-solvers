from pathlib import Path
import httpx


def file_response(file_content: bytes) -> httpx.Response:
    headers = {
        "Content-Type": "application/zip",
        "Content-Disposition": 'attachment; filename="data.zip"',
        "Content-Length": str(len(file_content)),
    }

    return httpx.Response(status_code=200, content=file_content, headers=headers)


def load_file(path: str) -> bytes:
    return Path(path).read_bytes()


def mock_get_request_content(mocker, file_contents: dict[str, bytes]):
    async def mocked_get_request(url: str) -> httpx.Response:
        if url in file_contents:
            content = file_contents[url]
            return file_response(content)
        else:
            raise ValueError("Unknown url")

    mocker.setattr("psp_solver_sdk.sat.process._make_get_request", mocked_get_request)
