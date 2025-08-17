import asyncio
from app.core.database import init_db, get_db
from sqlalchemy import text

async def check_tables():
    try:
        await init_db()
        async for db in get_db():
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'campaign_data'"))
            tables = result.fetchall()
            if tables:
                print(' campaign_data table exists')
                count_result = await db.execute(text("SELECT COUNT(*) FROM campaign_data"))
                count = count_result.scalar()
                print(f' campaign_data has {count} rows')
            else:
                print(' campaign_data table does not exist')
                print(' You need to create the tables first')
            break
    except Exception as e:
        print(f' Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_tables())
