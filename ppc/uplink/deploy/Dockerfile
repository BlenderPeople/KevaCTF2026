FROM python:3.12-slim
WORKDIR /app

COPY src/server.py src/tlv_func.py ./

RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "server.py"]
