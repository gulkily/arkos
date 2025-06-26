CREATE TYPE event_status AS ENUM ('CONFIRMED', 'TENTATIVE', 'CANCELLED');
CREATE TYPE event_classification AS ENUM ('PUBLIC', 'PRIVATE', 'CONFIDENTIAL');

CREATE TABLE calendars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    prod_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calendar_id UUID NOT NULL REFERENCES calendars(id) ON DELETE CASCADE,
    uid VARCHAR(255) NOT NULL UNIQUE,
    summary VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    url VARCHAR(2048),
    status event_status DEFAULT 'CONFIRMED',
    classification event_classification DEFAULT 'PUBLIC',
    priority SMALLINT CHECK (priority >= 0 AND priority <= 9),
    dtstart TIMESTAMPTZ NOT NULL,
    dtend TIMESTAMPTZ NOT NULL,
    dtstamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_all_day BOOLEAN DEFAULT FALSE,
    timezone TEXT NOT NULL DEFAULT 'UTC',
    CONSTRAINT valid_dates CHECK (dtend > dtstart)
);

CREATE TABLE event_categories (
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    category VARCHAR(255) NOT NULL,
    PRIMARY KEY (event_id, category)
);

CREATE TABLE recurring_rules (
    event_id UUID PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE,
    frequency VARCHAR(20) NOT NULL,
    interval_val INTEGER DEFAULT 1,
    until TIMESTAMPTZ,
    count INTEGER,
    byday TEXT[],
    bymonthday INTEGER[],
    bymonth INTEGER[],
    wkst VARCHAR(2),
    CONSTRAINT valid_interval CHECK (interval_val > 0),
    CONSTRAINT valid_count CHECK (count > 0)
);

CREATE INDEX events_calendar_id_idx ON events(calendar_id);
CREATE INDEX events_dtstart_idx ON events(dtstart);
CREATE INDEX events_dtend_idx ON events(dtend);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
