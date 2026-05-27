# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables to prevent Python from buffering output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django code
COPY . .

# Expose Django port
EXPOSE 8000

# Command to run Django server
# Note: 0.0.0.0 is required to allow Docker to route traffic to it
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]