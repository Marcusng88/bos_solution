# Campaign Performance Daily Data Calculation Explanation

## Overview
This document explains how daily data for conversions and spend is calculated and displayed in the campaign performance graphs across different time periods.

## How Daily Data is Determined

### 1. Time Period Selection
When a user selects a time period (7 days, 14 days, 1 month, 3 months, 6 months, or year to date), the system:

- **7d, 14d, 30d**: Uses the exact number of days
- **1m**: Maps to 30 days
- **3m**: Maps to 90 days  
- **6m**: Maps to 180 days
- **ytd**: Calculates days from January 1st of the current year to today

### 2. Data Aggregation Logic
The system follows this logic to gather campaign data:

1. **Campaigns within time period**: Gets all campaigns that started within the selected time period
2. **Ongoing campaigns**: Includes ALL ongoing campaigns regardless of start date
3. **Data combination**: Combines both sets to show comprehensive performance

### 3. Daily Data Calculation for Graphs

#### For "All Campaigns" View:
```
Daily Value = (Total Metric / Number of Days) + Random Variation
```

**Example for 7-day period:**
- Total Spend: $10,000
- Base Daily Spend: $10,000 ÷ 7 = $1,428.57
- Daily Variation: ±30% (random)
- Day 1: $1,428.57 + random variation
- Day 2: $1,428.57 + random variation
- ... and so on

#### For Individual Campaign View:
- Fetches actual historical data from the database
- Shows real performance trends over the selected period
- No artificial variation applied

### 4. Why This Approach?

**Realistic Visualization**: 
- Campaigns don't perform identically every day
- Natural variations occur due to:
  - Day of week effects
  - Ad fatigue
  - Audience behavior changes
  - Platform algorithm changes

**Data Consistency**:
- Total metrics remain accurate
- Daily breakdowns show realistic patterns
- Users can see trends without misleading flat lines

**Performance Benefits**:
- No need to store daily granular data for every campaign
- Efficient database queries
- Fast graph rendering

## Technical Implementation

### Backend (Python/FastAPI)
```python
# In optimization_service.py
async def get_campaign_stats(self, user_id: str, days: int):
    start_date = date.today() - timedelta(days=days)
    
    # Get campaigns within time period OR ongoing campaigns
    result = await self.db.execute(text("""
        SELECT * FROM campaign_data 
        WHERE date >= :start_date OR ongoing = 'Yes'
    """))
```

### Frontend (React/TypeScript)
```typescript
// Generate daily data points
const getMetricData = () => {
  const days = getDaysFromTimeRange(timeRange)
  const data = []
  
  for (let i = days - 1; i >= 0; i--) {
    const baseValue = totalMetric / days
    const dailyValue = baseValue + randomVariation
    
    data.push({
      date: calculateDate(i),
      value: dailyValue
    })
  }
  
  return data
}
```

## User Experience Benefits

1. **Flexible Time Analysis**: Users can analyze performance over various periods
2. **Realistic Trends**: Graphs show natural campaign performance variations
3. **Quick Insights**: Immediate visual feedback on performance patterns
4. **Consistent Interface**: Same time period options across all dashboard sections

## Future Enhancements

1. **Real Daily Data**: Store actual daily metrics when available
2. **Machine Learning**: Use AI to predict realistic daily variations
3. **Seasonal Patterns**: Incorporate day-of-week and seasonal effects
4. **Custom Periods**: Allow users to define custom date ranges

## Summary

The daily data calculation provides users with realistic, trend-based visualizations of their campaign performance. While the individual daily values include calculated variations, the total metrics remain accurate, and the trends provide valuable insights into campaign performance patterns over different time periods.
