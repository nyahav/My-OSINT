FROM postgres:16-alpine


RUN apk update && \
    apk add --no-cache python3 py3-pip libffi-dev openssl-dev \
    && pip install --no-cache-dir --break-system-packages bcrypt




