-- DealTracker Database Initialization Script
-- This script sets up the database schema and initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'America/New_York';

-- Create database if it doesn't exist (this is handled by Docker)
-- The database 'dealtracker' is created by the POSTGRES_DB environment variable

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dealtracker TO postgres;

-- Create initial schema (tables will be created by SQLAlchemy/Alembic)
-- This script just ensures the database is ready for the application

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'DealTracker database initialized successfully at %', NOW();
END $$; 