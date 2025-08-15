"""
Data Update Service
Periodically updates CSV files with fresh mock data to simulate real-time changes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from typing import Dict, List

class DataUpdateService:
    """Service to update mock data files periodically"""
    
    def __init__(self, data_path: str = "app/models/database/"):
        self.data_path = data_path
    
    def update_performance_metrics(self):
        """Add new daily performance data"""
        file_path = os.path.join(self.data_path, "performance_metrics.csv")
        
        try:
            df = pd.read_csv(file_path)
            
            # Get the last date
            last_date = pd.to_datetime(df['date'].iloc[-1])
            new_date = last_date + timedelta(days=1)
            
            # Generate new metrics with some variance
            new_row = {
                'date': new_date.strftime('%Y-%m-%d'),
                'our_posts': random.randint(1, 3),
                'our_engagement': random.randint(4000, 7000),
                'nike_posts': random.randint(1, 3),
                'nike_engagement': random.randint(6000, 9500),
                'adidas_posts': random.randint(1, 3),
                'adidas_engagement': random.randint(6000, 8500),
                'under_armour_posts': random.randint(1, 3),
                'under_armour_engagement': random.randint(6500, 9000),
                'puma_posts': random.randint(1, 3),
                'puma_engagement': random.randint(5000, 7500),
            }
            
            # Calculate industry average
            competitors = ['nike_engagement', 'adidas_engagement', 'under_armour_engagement', 'puma_engagement']
            new_row['industry_avg_engagement'] = np.mean([new_row[comp] for comp in competitors])
            
            # Add new row and keep only last 30 days
            df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df_final = df_new.tail(30)
            
            # Save back to file
            df_final.to_csv(file_path, index=False)
            print(f"Updated performance metrics with data for {new_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def simulate_competitor_activity(self):
        """Add new competitor content entries"""
        file_path = os.path.join(self.data_path, "competitor_content.csv")
        
        # This would add new competitor content entries
        # Implementation depends on the structure of your competitor_content.csv
        pass
    
    def update_content_gaps(self):
        """Update content gaps with slight variations"""
        file_path = os.path.join(self.data_path, "content_gaps.csv")
        
        try:
            df = pd.read_csv(file_path)
            
            # Add small random variations to opportunity scores
            df['opportunity_score'] = df['opportunity_score'] + np.random.normal(0, 0.1, len(df))
            df['opportunity_score'] = np.clip(df['opportunity_score'], 0, 10)
            
            # Occasionally shift gap percentages slightly
            df['gap_percentage'] = df['gap_percentage'] + np.random.normal(0, 2, len(df))
            
            df.to_csv(file_path, index=False)
            print("Updated content gaps with new opportunity scores")
            
        except Exception as e:
            print(f"Error updating content gaps: {e}")
    
    def run_daily_update(self):
        """Run all daily updates"""
        print(f"Starting daily data update at {datetime.now()}")
        self.update_performance_metrics()
        self.update_content_gaps()
        print("Daily update completed")

if __name__ == "__main__":
    # This can be run as a scheduled task
    service = DataUpdateService()
    service.run_daily_update()
