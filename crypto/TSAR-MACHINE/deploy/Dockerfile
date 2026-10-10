FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=60606

WORKDIR /app

COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py ./
COPY src/templates ./templates
COPY src/static ./static
COPY src/notes ./notes
EXPOSE 60606
CMD ["python", "app.py"]
