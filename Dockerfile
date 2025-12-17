FROM python:3.11-slim

# Install system dependencies required by LightGBM (libgomp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Set workdir so that src/api.py can still load ../artifacts/*
WORKDIR /app/src

# Copy the whole project into the image
COPY . /app

# Install Python dependencies for the API
RUN pip install --no-cache-dir -r /app/src/requirements.txt

# Default command; use PORT if provided by the platform, else 8000.
# Using sh -c so ${PORT:-8000} is expanded at runtime.
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]


