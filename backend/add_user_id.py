import asyncio
from app.core.database import init_db, get_db
from sqlalchemy import text

async def add_user_id_column():
    try:
        await init_db()
        async for db in get_db():
            print(' Adding user_id column to campaign_data table...')
            
            # Add the user_id column
            await db.execute(text("ALTER TABLE campaign_data ADD COLUMN user_id VARCHAR(255) NOT NULL DEFAULT 'demo_user_123'"))
            
            # Create index
            await db.execute(text("CREATE INDEX IF NOT EXISTS idx_campaign_data_user_id ON campaign_data(user_id)"))
            
            # Commit the changes
            await db.commit()
            
            print(' Successfully added user_id column!')
            print(' Checking updated table structure...')
            
            # Verify the column was added
            result = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'campaign_data' ORDER BY ordinal_position"))
            columns = result.fetchall()
            print(' Updated campaign_data table columns:')
            for col in columns:
                print(f'  - {col[0]} ({col[1]})')
            break
    except Exception as e:
        print(f' Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(add_user_id_column())
