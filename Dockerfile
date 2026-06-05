FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app and frontend static files
COPY backend/app ./backend/app
COPY frontend ./frontend

# Expose port
EXPOSE 8000

# Set environment paths
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Ensure logs directory exists
RUN mkdir -p /app/backend/logs

# Run the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
