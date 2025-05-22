#!/bin/bash
set -e

# Wait for MySQL to be ready
echo "Waiting for MySQL to start..."
until mysql -h "localhost" -u "root" -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; do
  echo "MySQL is unavailable - sleeping"
  sleep 5
done
echo "MySQL is up and running!"

# Hash the admin user's password using Python and bcrypt
# The bcrypt hash is directly stored in the database, no base64 encoding needed for MySQL.
ADMIN_PASSWORD_HASH=$(python3 -c "
import bcrypt
password = '$MYSQL_ADMIN_PASSWORD'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(hashed.decode('utf-8'))")

echo "Creating database and user table..."
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE \`${MYSQL_DATABASE}\`;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    admin BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(255),
    created_date DATETIME,
    updated_by VARCHAR(255),
    updated_date DATETIME
);

-- Insert admin user (replace values as needed)
INSERT INTO users (username, hashed_password, email, first_name, last_name, admin, active, created_by, created_date, updated_by, updated_date)
VALUES ('$MYSQL_ADMIN_USERNAME', '$ADMIN_PASSWORD_HASH', '$MYSQL_ADMIN_EMAIL', 'admin', 'admin', TRUE, TRUE, '$MYSQL_ADMIN_USERNAME', NOW(), '$MYSQL_ADMIN_USERNAME', NOW())
ON DUPLICATE KEY UPDATE
    hashed_password = VALUES(hashed_password),
    email = VALUES(email),
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    admin = VALUES(admin),
    active = VALUES(active),
    updated_by = VALUES(updated_by),
    updated_date = NOW();

-- Create a dedicated application user and grant privileges
CREATE USER IF NOT EXISTS '$MYSQL_USER'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '$MYSQL_USER'@'%';
FLUSH PRIVILEGES;
EOF

echo "Database and user table setup complete, and application user created."
