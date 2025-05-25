#!/bin/bash
set -e

# These variables are automatically available from the PostgreSQL Docker image if set in docker-compose.yml
# PGPASSWORD=${POSTGRES_PASSWORD} # You might need this explicitly if not relying on defaults

echo "Waiting for PostgreSQL to start..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 5
done
echo "PostgreSQL is up and running!"

# Hash the admin user's password using Python and bcrypt
# Ensure bcrypt is installed in the PostgreSQL container's Dockerfile (Dockerfile.postgres)
ADMIN_PASSWORD_HASH=$(python3 -c "
import bcrypt
password = '$POSTGRES_ADMIN_PASSWORD'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(hashed.decode('utf-8'))")

echo "Creating database and user..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE admin WITH LOGIN PASSWORD 'adminpass';
    ALTER ROLE admin CREATEDB;
    -- Optional: if you want `postgres` to exist too
    CREATE ROLE postgres WITH LOGIN PASSWORD 'password';
    ALTER ROLE postgres CREATEDB;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Create a dedicated application user and grant privileges
    CREATE USER ${POSTGRES_APP_USER} WITH PASSWORD '${POSTGRES_APP_PASSWORD}';
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_APP_USER};

    -- Connect to the newly created application database
    \c ${POSTGRES_DB}

    -- Create the users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        hashed_password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        admin BOOLEAN DEFAULT FALSE,
        active BOOLEAN DEFAULT TRUE,
        created_by VARCHAR(255),
        created_date TIMESTAMP WITHOUT TIME ZONE,
        updated_by VARCHAR(255),
        updated_date TIMESTAMP WITHOUT TIME ZONE
    );

    -- Insert admin user (ON CONFLICT handles updates if user already exists)
    INSERT INTO users (username, hashed_password, email, first_name, last_name, admin, active, created_by, created_date, updated_by, updated_date)
    VALUES ('${POSTGRES_ADMIN_USERNAME}', '${ADMIN_PASSWORD_HASH}', '${POSTGRES_ADMIN_EMAIL}', 'admin', 'admin', TRUE, TRUE, '${POSTGRES_ADMIN_USERNAME}', NOW(), '${POSTGRES_ADMIN_USERNAME}', NOW())
    ON CONFLICT (username) DO UPDATE SET
        hashed_password = EXCLUDED.hashed_password,
        email = EXCLUDED.email,
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        admin = EXCLUDED.admin,
        active = EXCLUDED.active,
        updated_by = EXCLUDED.updated_by,
        updated_date = NOW();

EOSQL

echo "Database, user, and table setup complete for PostgreSQL."