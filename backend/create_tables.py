import asyncio
from app.core.database import init_db, get_db
from sqlalchemy import text

async def create_optimization_tables():
    try:
        await init_db()
        async for db in get_db():
            print(' Creating optimization tables...')
            
            # Create optimization_alerts table
            await db.execute(text(\"\"\"
                CREATE TABLE IF NOT EXISTS optimization_alerts (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) NOT NULL,
                    campaign_name VARCHAR(255),
                    alert_type VARCHAR(50) NOT NULL,
                    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    recommendation TEXT,
                    alert_data TEXT,
                    is_read BOOLEAN DEFAULT FALSE,
                    is_dismissed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    read_at TIMESTAMPTZ,
                    dismissed_at TIMESTAMPTZ
                )
            \"\"\"))
            
            # Create risk_patterns table
            await db.execute(text(\"\"\"
                CREATE TABLE IF NOT EXISTS risk_patterns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) NOT NULL,
                    campaign_name VARCHAR(255) NOT NULL,
                    pattern_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(10) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                    detected_at TIMESTAMPTZ DEFAULT NOW(),
                    pattern_data TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMPTZ
                )
            \"\"\"))
            
            # Create optimization_recommendations table
            await db.execute(text(\"\"\"
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) NOT NULL,
                    campaign_name VARCHAR(255),
                    recommendation_type VARCHAR(50) NOT NULL,
                    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    action_items TEXT,
                    potential_impact TEXT,
                    confidence_score DECIMAL(3,2) DEFAULT 0.0,
                    is_applied BOOLEAN DEFAULT FALSE,
                    applied_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            \"\"\"))
            
            # Create indexes
            await db.execute(text(\"CREATE INDEX IF NOT EXISTS idx_optimization_alerts_user_id ON optimization_alerts(user_id)\"))
            await db.execute(text(\"CREATE INDEX IF NOT EXISTS idx_risk_patterns_user_id ON risk_patterns(user_id)\"))
            await db.execute(text(\"CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_user_id ON optimization_recommendations(user_id)\"))
            
            await db.commit()
            
            print(' Successfully created all optimization tables!')
            
            # Verify tables were created
            result = await db.execute(text(\"\"\"
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('optimization_alerts', 'risk_patterns', 'optimization_recommendations')
                ORDER BY table_name
            \"\"\"))
            tables = result.fetchall()
            print(' Created tables:')
            for table in tables:
                print(f'   {table[0]}')
            break
    except Exception as e:
        print(f' Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(create_optimization_tables())
