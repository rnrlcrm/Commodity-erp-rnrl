-- Database initialization script
-- Runs once when the container is first created

-- Enable pgvector extension for vector similarity search (AI/ML features)
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant necessary permissions to commodity_user
GRANT ALL PRIVILEGES ON DATABASE commodity_erp TO commodity_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO commodity_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO commodity_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO commodity_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO commodity_user;
