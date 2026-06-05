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