# Science Data Kit (SDK) Dockerfile
# This Dockerfile builds the main Science Data Kit application container

FROM python:3.9-slim

LABEL maintainer="Science Data Kit Team <info@sciencedatakit.org>"
LABEL description="Science Data Kit - A comprehensive tool for scientific data analysis"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=science_data_kit.web.app \
    FLASK_ENV=production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Expose the port Flask runs on
EXPOSE 5001

# Set up entrypoint
COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Run the application
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "run_flask.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:5001/health || exit 1
