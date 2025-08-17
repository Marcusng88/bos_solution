import asyncio
from app.core.database import init_db, get_db
from sqlalchemy import text

async def check_columns():
    try:
        await init_db()
        async for db in get_db():
            result = await db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'campaign_data' ORDER BY ordinal_position"))
            columns = result.fetchall()
            print(' Current campaign_data table columns:')
            for col in columns:
                print(f'  - {col[0]} ({col[1]})')
            break
    except Exception as e:
        print(f' Error: {e}')

asyncio.run(check_columns())
