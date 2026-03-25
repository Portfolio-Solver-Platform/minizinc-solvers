FROM --platform=linux/amd64 python:3.14-slim@sha256:fb83750094b46fd6b8adaa80f66e2302ecbe45d513f6cece637a841e1025b4ca AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Set the path for MiniZinc so the system can find it
    PATH="/opt/minizinc/bin:$PATH"

# Install uv (Copy from official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install MiniZinc
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    # Download and install MiniZinc
    && mkdir -p /opt/minizinc \
    && curl -L https://github.com/MiniZinc/MiniZincIDE/releases/download/2.9.4/MiniZincIDE-2.9.4-bundle-linux-x86_64.tgz \
    | tar xz -C /opt/minizinc --strip-components=1

# Create User
RUN useradd -u 10001 -m appuser

WORKDIR /home/appuser/app

COPY ./pyproject.toml .
COPY ./uv.lock .

# Change ownership so appuser can write to the directory during 'uv sync'
RUN chown -R appuser:appuser /home/appuser/app

USER 10001

# Add the virtual environment to PATH (uv creates .venv by default)
ENV PATH="/home/appuser/app/.venv/bin:$PATH"

# -----------------------------------------------------------
FROM base AS dev

RUN uv sync --frozen

COPY --chown=appuser:appuser ./psp_solver_sdk/ ./psp_solver_sdk/
COPY --chown=appuser:appuser ./src/ ./src/
COPY --chown=appuser:appuser ./tests/ ./tests/

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]

# -----------------------------------------------------------
FROM base AS runtime

RUN uv sync --frozen --no-dev

COPY --chown=appuser:appuser ./psp_solver_sdk/ ./psp_solver_sdk/
COPY --chown=appuser:appuser ./src/ ./src/

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]
