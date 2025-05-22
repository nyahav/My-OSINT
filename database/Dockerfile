# Use a MySQL 8.0 base image
FROM mysql:8.0

# Install Python and bcrypt for password hashing
# We need python3-pip to install bcrypt
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install bcrypt library
RUN pip3 install bcrypt

# Copy the initialization script into the Docker entrypoint directory
# This ensures the script runs when the MySQL container starts
COPY init-mysql.sh /docker-entrypoint-initdb.d/

# Ensure the script is executable
RUN chmod +x /docker-entrypoint-initdb.d/init-mysql.sh
