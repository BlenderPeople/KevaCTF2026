FROM python:3.12-slim
WORKDIR /app

COPY src/main.py ./

RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]
