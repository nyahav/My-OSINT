
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres'
   ) THEN
      EXECUTE format('CREATE USER postgres WITH PASSWORD %L', current_setting('osint.user_password', true));
   END IF;
END
$do$;

GRANT ALL ON SCHEMA public TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;

