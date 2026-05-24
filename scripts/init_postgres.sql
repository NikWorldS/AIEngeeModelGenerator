CREATE TABLE IF NOT EXISTS requests (
    id BIGSERIAL PRIMARY KEY,
    request_id UUID NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_text TEXT NOT NULL,
    response_text TEXT NULL,
    duration DOUBLE PRECISION NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_type TEXT NULL,
    error_message TEXT NULL,

    CONSTRAINT ck_requests_status
        CHECK (status IN ('pending', 'success', 'error'))
);

CREATE OR REPLACE FUNCTION set_requests_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_requests_set_updated_at ON requests;

CREATE TRIGGER trg_requests_set_updated_at
BEFORE UPDATE ON requests
FOR EACH ROW
EXECUTE FUNCTION set_requests_updated_at();