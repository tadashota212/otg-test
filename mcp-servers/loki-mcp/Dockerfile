FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp httpx uvicorn fastapi

COPY server.py .

CMD ["python", "-u", "-m", "server"]
