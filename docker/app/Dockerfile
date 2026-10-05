FROM ghcr.io/astral-sh/uv:0.9.11-python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update \
    && apt-get install --no-install-recommends --yes make postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd --gid "${APP_GID}" app \
    && useradd --no-log-init --create-home --uid "${APP_UID}" --gid "${APP_GID}" app \
    && mkdir -p /app /opt/venv \
    && chown -R app:app /app /opt/venv

WORKDIR /app

COPY --chown=app:app pyproject.toml uv.lock ./

USER app

RUN uv sync --frozen --extra dev --no-install-project

COPY --chown=app:app . .
RUN uv sync --frozen --extra dev

COPY --chown=app:app --chmod=755 docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
