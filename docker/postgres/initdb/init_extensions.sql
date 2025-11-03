-- Init script run by postgres container on first startup
-- Create database, user and enable pgvector and pg_trgm extensions

CREATE USER voltedge WITH PASSWORD 'voltedge';
CREATE DATABASE voltedge OWNER voltedge;
\connect voltedge;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
