FROM jobork/parasol@sha256:34494599d825894a48f68f36111dc25ec01e91e2247fe7f3449ded19d7bbe4ce AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Remove bundled OpenSSL that conflicts with the system version Python was compiled against
RUN find /opt -name 'libcrypto*' -delete -o -name 'libssl*' -delete && ldconfig

# Install uv (Copy from official image)
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 /uv /usr/local/bin/uv

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
