FROM python:3.12 AS builder
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY src/pyproject.toml src/uv.lock ./

RUN uv venv && uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/main.py ./
COPY src/.env.admin ./.env.admin
COPY src/templates/ ./templates/
COPY src/static/ ./static/
COPY src/src/ ./src/

RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]