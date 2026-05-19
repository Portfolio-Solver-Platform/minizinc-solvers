FROM jobork/parasol@sha256:45f793dd283d9044bc21d3c2fb7f0031b81c3def5b273d63a283cc8cbaa2a9df AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Remove bundled OpenSSL that conflicts with the system version Python was compiled against
RUN find /opt -name 'libcrypto*' -delete -o -name 'libssl*' -delete && ldconfig

# Install uv (Copy from official image)
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:e590846f4776907b254ac0f44b5b380347af5d90d668138ca7938d1b0c2f98d3 /uv /usr/local/bin/uv

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
