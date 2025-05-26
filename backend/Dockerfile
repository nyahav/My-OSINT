# Stage 1 - Build requirements using Poetry
FROM python:3.11-alpine AS builder

# Install dependencies
RUN apk add --no-cache curl gcc musl-dev libffi-dev openssl-dev build-base

# Install Poetry
RUN pip install poetry && poetry self add poetry-plugin-export

# Copy Poetry files
COPY pyproject.toml poetry.lock /app/
WORKDIR /app

# Export requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev

# Stage 2 - Final runtime image
FROM python:3.11-alpine

# Install runtime dependencies including tools for network operations
RUN apk add --no-cache \
    libpq \
    postgresql-libs \
    curl \
    wget \
    ca-certificates \
    docker-cli

# Create non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /home/app

# Copy requirements and install
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY ./app ./app
COPY ./pyproject.toml .

# Create shared directory for communication with tools container
RUN mkdir -p /home/app/shared && chown -R appuser:appgroup /home/app/shared

# Use the non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]