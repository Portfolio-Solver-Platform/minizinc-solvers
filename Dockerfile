FROM nixos/nix:latest

WORKDIR /app

# Enable experimental features for Nix
RUN mkdir -p /etc/nix && echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

COPY problems ./problems
COPY flake.nix flake.lock pyproject.toml uv.lock ./
COPY src ./src

EXPOSE 8080

CMD ["nix", "develop", "-c", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--workers", "4", "src.main:app"]
