FROM postgres:16-alpine

# Optional: Install Python and bcrypt if needed for DB container (though this is unusual for DB containers)
RUN apk update && \
    apk add --no-cache python3 py3-pip libffi-dev openssl-dev \
    && pip install --no-cache-dir --break-system-packages bcrypt




