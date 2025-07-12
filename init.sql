-- Initialize Statify Database
CREATE DATABASE statify;

-- Connect to the statify database
\c statify;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for common queries (will be created by SQLAlchemy but good to have)
-- These will be created after tables are set up

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE statify TO statify_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO statify_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO statify_user;

-- Set default permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO statify_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO statify_user;