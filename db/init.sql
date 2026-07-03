CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workflow_name TEXT NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    graph_json JSONB NOT NULL DEFAULT '{}'::jsonb,

    execution_flow JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS executions (

    reference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    workflow_id TEXT NOT NULL,

    start_at TIMESTAMPTZ,

    finish_at TIMESTAMPTZ,

    current_state TEXT NOT NULL
    
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_updated_at
BEFORE UPDATE ON workflows
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();