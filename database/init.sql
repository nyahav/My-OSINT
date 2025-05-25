-- Create user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres '
   ) THEN
      CREATE USER postgres  WITH PASSWORD 'password';
   END IF;
END
$do$;