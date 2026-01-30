FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
# Railway sets PORT env var
ENV PORT=8000
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
