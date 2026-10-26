-- Runs once, on the first start of the database container.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
  id            text PRIMARY KEY,               -- for example returns-policy#0
  doc           text NOT NULL,                  -- source document
  section       text,                           -- section path inside the document
  chunk_index   integer NOT NULL,
  content       text NOT NULL,                  -- the chunk text shown as a source
  metadata      jsonb NOT NULL DEFAULT '{}',    -- region, effective date, ...
  access_group  text NOT NULL DEFAULT 'public', -- filter on this for every search
  embed_model   text NOT NULL,                  -- for example bge-m3; re-embed when it changes
  embedding     vector(1024) NOT NULL           -- 1024 matches bge-m3
);

-- Approximate nearest-neighbour index for cosine similarity search.
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
  ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_access_group_idx ON chunks (access_group);
