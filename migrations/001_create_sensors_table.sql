CREATE TABLE IF NOT EXISTS sensors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    type VARCHAR(128) NOT NULL,
    unit VARCHAR(64),
    min_value NUMERIC,
    max_value NUMERIC,
    device_id UUID NOT NULL REFERENCES devices(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sensors_name ON sensors (name);
CREATE INDEX IF NOT EXISTS ix_sensors_type ON sensors (type);
CREATE INDEX IF NOT EXISTS ix_sensors_unit ON sensors (unit);
CREATE INDEX IF NOT EXISTS ix_sensors_device_id ON sensors (device_id);
CREATE INDEX IF NOT EXISTS ix_sensors_created_at ON sensors (created_at);
