"use client"

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { roiApi } from '@/lib/api-client';
import { TimeRange } from '@/lib/api-client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface ROITrendsProps {
  range: TimeRange;
}

interface DataPoint {
  ts: string;
  roi: number;
}

interface BackendResponse {
  all_data: Array<{
    created_at: string;
    roi_percentage: number;
    platform: string;
    user_id: string;
  }>;
  message: string;
}

export default function ROITrends({ range }: ROITrendsProps) {
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log(`🚀 Frontend: Fetching ROI trends for range: ${range}`);
        
        // Fetch ALL data from backend (no date filtering)
        const response = await roiApi.roiTrends(range);
        console.log(`📊 Backend response:`, response);
        
        if ('all_data' in response) {
          // Frontend filtering logic - this is the key change!
          const allData = response.all_data;
          console.log(`📊 Total rows received: ${allData.length}`);
          
          // Filter data based on the selected range
          const filteredData = filterDataByRange(allData, range);
          console.log(`📊 Filtered data for ${range}: ${filteredData.length} rows`);
          
          // Group by date and calculate average ROI
          const dailyROI = groupByDateAndCalculateROI(filteredData);
          console.log(`📊 Daily ROI data: ${dailyROI.length} days`);
          
          setData(dailyROI);
        } else {
          console.error('❌ Unexpected response format:', response);
          setError('Unexpected response format from backend');
        }
      } catch (err) {
        console.error('❌ Error fetching ROI trends:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [range]);

  // Frontend filtering function - handles 7d, 14d, 30d, 90d logic
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()); // Start of today
    
    // Calculate start date based on range (exclude today's incomplete data)
    let startDate: Date;
    switch (selectedRange) {
      case '7d':
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '14d':
        startDate = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    }
    
    console.log(`📅 Frontend filtering: ${startDate.toISOString()} to ${today.toISOString()}`);
    
    // Filter data within the range
    return allData.filter(row => {
      const rowDate = new Date(row.created_at);
      return rowDate >= startDate && rowDate < today; // Exclude today
    });
  };

  // Group filtered data by date and calculate average ROI
  const groupByDateAndCalculateROI = (filteredData: any[]): DataPoint[] => {
    const dailyGroups: { [key: string]: number[] } = {};
    
    // Group ROI values by date
    filteredData.forEach(row => {
      if (row.roi_percentage !== null && row.roi_percentage !== undefined) {
        const dateKey = row.created_at.split('T')[0]; // YYYY-MM-DD
        if (!dailyGroups[dateKey]) {
          dailyGroups[dateKey] = [];
        }
        dailyGroups[dateKey].push(parseFloat(row.roi_percentage));
      }
    });
    
    // Calculate average ROI per day and convert to chart format
    const result: DataPoint[] = Object.keys(dailyGroups)
      .sort()
      .map(dateKey => {
        const avgROI = dailyGroups[dateKey].reduce((sum, val) => sum + val, 0) / dailyGroups[dateKey].length;
        return {
          ts: `${dateKey}T00:00:00Z`,
          roi: Math.round(avgROI * 100) / 100 // Round to 2 decimal places
        };
      });
    
    console.log(`📊 Daily ROI calculation: ${result.length} days processed`);
    return result;
  };

  if (loading) {
    return <div className="text-center py-8">Loading ROI trends...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">Error: {error}</div>;
  }

  if (!data || data.length === 0) {
    return <div className="text-center py-8 text-gray-500">No ROI data available for the selected range</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>ROI Trends</CardTitle>
        <CardDescription>Return on investment over time vs industry benchmark</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
              <XAxis 
                dataKey="ts" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                  color: '#ffffff'
                }}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
                formatter={(value: number) => [`${Number(value).toFixed(1)}%`, 'ROI']}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Line 
                type="monotone" 
                dataKey="roi" 
                stroke="#8b5cf6" 
                strokeWidth={3}
                dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#8b5cf6', stroke: '#ffffff', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 text-sm text-muted-foreground text-center">
          Showing {data.length} days of ROI data 
        </div>
      </CardContent>
    </Card>
  );
}
