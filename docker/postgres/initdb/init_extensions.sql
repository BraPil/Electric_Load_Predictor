-- VoltEdge Postgres Initialization Script
-- Creates database, user, and enables extensions for RAG, vector search, and multi-tenant isolation

-- Create application user and database
CREATE USER voltedge WITH PASSWORD 'voltedge';
CREATE DATABASE voltedge OWNER voltedge;

-- Connect to voltedge database to install extensions
\connect voltedge;

-- Enable pgvector extension for ANN (Approximate Nearest Neighbor) search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for trigram-based full-text search (FTS)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable btree_gist for additional indexing capabilities
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Grant schema usage to voltedge user
GRANT ALL PRIVILEGES ON DATABASE voltedge TO voltedge;
GRANT ALL ON SCHEMA public TO voltedge;

-- Log initialization completion
DO $$
BEGIN
  RAISE NOTICE 'VoltEdge database initialized: user=voltedge, extensions=vector,pg_trgm,btree_gist';
END
$$;
