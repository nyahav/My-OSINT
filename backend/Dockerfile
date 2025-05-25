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

# Install only runtime dependencies
RUN apk add --no-cache libpq postgresql-libs

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /home/app

# Copy requirements and install
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY ./app ./app
COPY ./pyproject.toml .

# Use non-root user
USER appuser

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
