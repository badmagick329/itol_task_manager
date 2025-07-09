FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY ./.env .

ENV FLASK_APP="src.web.app:create_app"
RUN flask init-db

CMD ["python3", "./src/main.py"]
