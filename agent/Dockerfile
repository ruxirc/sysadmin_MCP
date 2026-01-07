FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY agent/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./agent agent

ENV UVICORN_HOST=0.0.0.0
CMD ["adk", "web", "--host", "0.0.0.0"]