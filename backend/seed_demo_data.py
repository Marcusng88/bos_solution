#!/usr/bin/env python3
"""
Demo data seeder for self-optimization testing
Creates sample campaign data in the campaign_data table
"""

import asyncio
import random
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import init_db, get_db, ModelBase, engine
from app.models.campaign import CampaignData


async def create_tables():
    """Create all tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(ModelBase.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


async def seed_campaign_data():
    """Seed demo campaign data"""
    
    # Sample campaign names
    campaigns = [
        "Summer Sale",
        "Brand Awareness", 
        "Retargeting Campaign",
        "Mobile Campaign",
        "Black Friday Prep",
        "Holiday Special",
        "Spring Collection",
        "Back to School"
    ]
    
    # Generate data for the last 30 days
    start_date = date.today() - timedelta(days=30)
    
    async for db in get_db():
        try:
            for i in range(30):
                current_date = start_date + timedelta(days=i)
                
                for campaign_name in campaigns:
                    # Vary performance metrics to create realistic patterns
                    base_impressions = random.randint(5000, 20000)
                    base_ctr = random.uniform(0.5, 4.0)  # 0.5% to 4.0% CTR
                    base_cpc = random.uniform(1.0, 6.0)  # $1.00 to $6.00 CPC
                    
                    # Add some campaigns with issues for testing
                    if campaign_name == "Brand Awareness" and i > 20:
                        base_ctr = random.uniform(0.3, 0.8)  # Low CTR
                        base_cpc = random.uniform(4.0, 7.0)  # High CPC
                    
                    if campaign_name == "Mobile Campaign" and i > 25:
                        base_impressions *= 1.8  # Spending spike
                    
                    clicks = int(base_impressions * (base_ctr / 100))
                    spend = Decimal(str(round(clicks * base_cpc, 2)))
                    budget = spend * Decimal(str(random.uniform(1.0, 1.3)))  # Budget 0-30% higher than spend
                    
                    # Sometimes exceed budget for testing
                    if random.random() < 0.1:  # 10% chance
                        spend = budget * Decimal(str(random.uniform(1.05, 1.2)))  # 5-20% overspend
                    
                    conversions = max(0, int(clicks * random.uniform(0.02, 0.08)))  # 2-8% conversion rate
                    
                    # Some campaigns have zero conversions for testing
                    if campaign_name == "Brand Awareness" and i > 20:
                        conversions = 0
                    
                    # Mark recent campaigns as ongoing
                    ongoing = "Yes" if i >= 25 else "No"
                    if campaign_name in ["Summer Sale", "Retargeting Campaign", "Mobile Campaign"]:
                        ongoing = "Yes"
                    
                    campaign_data = CampaignData(
                        user_id="demo_user_123",  # Demo user ID
                        name=campaign_name,
                        date=current_date,
                        impressions=base_impressions,
                        clicks=clicks,
                        ctr=Decimal(str(round(base_ctr, 4))),
                        cpc=Decimal(str(round(base_cpc, 2))),
                        spend=spend,
                        budget=budget,
                        conversions=conversions,
                        ongoing=ongoing
                    )
                    
                    db.add(campaign_data)
            
            await db.commit()
            print(f"✅ Seeded campaign data for {len(campaigns)} campaigns over 30 days")
            
        except Exception as e:
            print(f"❌ Error seeding campaign data: {e}")
            await db.rollback()
            raise
        finally:
            break  # Exit the async generator


async def main():
    """Main seeder function"""
    try:
        print("🚀 Starting demo data seeding...")
        
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Create tables
        await create_tables()
        
        # Seed campaign data
        await seed_campaign_data()
        
        print("🎉 Demo data seeding completed successfully!")
        print("\nYou can now test the self-optimization features with:")
        print("- 8 different campaigns")
        print("- 30 days of historical data")
        print("- Various performance patterns (good, bad, spikes, overspends)")
        print("- Ongoing and paused campaigns")
        
    except Exception as e:
        print(f"💥 Error during seeding: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
