FROM python:3.11-alpine AS builder


RUN apk add --no-cache curl gcc musl-dev libffi-dev openssl-dev build-base


RUN pip install poetry && poetry self add poetry-plugin-export

COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev

FROM python:3.11-alpine

RUN apk add --no-cache \
    libpq \
    postgresql-libs \
    curl \
    wget \
    ca-certificates \
    docker-cli

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /home/app

COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./pyproject.toml .

RUN mkdir -p /home/app/shared && chown -R appuser:appgroup /home/app/shared

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]