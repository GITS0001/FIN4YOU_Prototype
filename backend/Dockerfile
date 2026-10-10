FROM python:3.12-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend /app/backend
COPY data /app/data
COPY ml /app/ml

EXPOSE 8000

ENV PYTHONPATH=/app/backend

# The command needs to run from /app/backend to match app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
