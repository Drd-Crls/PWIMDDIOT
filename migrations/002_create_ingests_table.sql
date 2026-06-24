CREATE TABLE IF NOT EXISTS ingests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metadata JSONB NOT NULL,
    sensor_id UUID NOT NULL REFERENCES sensors(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ingests_sensor_id ON ingests (sensor_id);
CREATE INDEX IF NOT EXISTS ix_ingests_created_at ON ingests (created_at);
CREATE INDEX IF NOT EXISTS ix_ingests_sensor_id_created_at ON ingests (sensor_id, created_at);
CREATE INDEX IF NOT EXISTS ix_ingests_metadata ON ingests USING GIN (metadata);
