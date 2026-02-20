# Use the official Python image
FROM python:3.12.4-slim

# Prevent .pyc files and ensure logs show immediately
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Cloud Run port
EXPOSE 8080

# Start Gunicorn using the Cloud Run PORT env var
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 0 sejong_backend.wsgi:application