-- Triggers for updated_at on ROI tables

-- Ensure trigger function exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Campaign table trigger
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='campaign_with_user_id'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_campaign_with_user_id_updated_at'
        ) THEN
            DROP TRIGGER trg_campaign_with_user_id_updated_at ON campaign_with_user_id;
        END IF;
        CREATE TRIGGER trg_campaign_with_user_id_updated_at
        BEFORE UPDATE ON campaign_with_user_id
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;

-- ROI metrics table trigger
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='roi_metrics'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_roi_metrics_updated_at'
        ) THEN
            DROP TRIGGER trg_roi_metrics_updated_at ON roi_metrics;
        END IF;
        CREATE TRIGGER trg_roi_metrics_updated_at
        BEFORE UPDATE ON roi_metrics
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;

-- Platform metrics table trigger
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='platform_metrics'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_platform_metrics_updated_at'
        ) THEN
            DROP TRIGGER trg_platform_metrics_updated_at ON platform_metrics;
        END IF;
        CREATE TRIGGER trg_platform_metrics_updated_at
        BEFORE UPDATE ON platform_metrics
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END$$;


