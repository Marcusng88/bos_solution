"use client"

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { roiApi } from '@/lib/api-client';
import { TimeRange } from '@/lib/api-client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface ChannelPerformanceProps {
  userId: string;
  range: TimeRange;
}

interface ChannelData {
  platform: string;
  impressions: number;
  engagement: number;
  revenue: number;
  spend: number;
  total_clicks: number;
  avg_roi: number;
  profit: number;
  engagement_rate: number;
  click_through_rate: number;
  efficiency_score: number;
}

interface BackendResponse {
  all_data: Array<{
    platform: string;
    views: number;
    likes: number;
    comments: number;
    shares: number;
    clicks: number;
    revenue_generated: number;
    ad_spend: number;
    roi_percentage: number;
    created_at: string;
  }>;
  message: string;
}

export default function ChannelPerformance({ userId, range }: ChannelPerformanceProps) {
  const [data, setData] = useState<ChannelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log(`🚀 Frontend: Fetching channel performance for range: ${range}`);
        
        // Fetch ALL data from backend (no date filtering)
        const response = await roiApi.channelPerformance(userId, range);
        console.log(`📊 Backend response:`, response);
        
        if (response && typeof response === 'object' && 'all_data' in response) {
          // Frontend filtering logic - this is the key change!
          const allData = Array.isArray((response as any).all_data) ? (response as any).all_data : [];
          console.log(`📊 Total rows received: ${allData.length}`);
          
          // Filter data based on the selected range
          const filteredData = filterDataByRange(allData, range);
          console.log(`📊 Filtered data for ${range}: ${filteredData.length} rows`);
          
          // Process data and calculate metrics
          const channelMetrics = processChannelData(filteredData);
          console.log(`📊 Channel metrics calculated: ${channelMetrics.length} platforms`);
          
          setData(channelMetrics);
        } else {
          console.error('❌ Unexpected response format:', response);
          setError('Unexpected response format from backend');
        }
      } catch (err) {
        console.error('❌ Error fetching channel performance:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId, range]);

  // Frontend filtering function - handles 7d, 30d, 90d logic
  const filterDataByRange = (allData: any[], selectedRange: TimeRange) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()); // Start of today
    
    // Calculate start date based on range (exclude today's incomplete data)
    let startDate: Date;
    switch (selectedRange) {
      case '7d':
        startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
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
      const ts = row.created_at || row.update_timestamp;
      if (!ts) return false;
      const rowDate = new Date(ts);
      return rowDate >= startDate && rowDate < today; // Exclude today
    });
  };

  // Process filtered data and calculate channel metrics
  const processChannelData = (filteredData: any[]): ChannelData[] => {
    if (!Array.isArray(filteredData)) return [];
    const platformMetrics: { [key: string]: any } = {};
    
    // Group data by platform and accumulate metrics
    filteredData.forEach(row => {
      if (!row || typeof row !== 'object') return;
      const platform = row.platform || 'unknown';
      if (!platformMetrics[platform]) {
        platformMetrics[platform] = {
          impressions: 0,
          engagement: 0,
          revenue: 0,
          spend: 0,
          clicks: 0,
          roi_values: []
        };
      }
      
      const views = Number(row.views || 0);
      const likes = Number(row.likes || 0);
      const comments = Number(row.comments || 0);
      const shares = Number(row.shares || 0);
      const revenue = Number(row.revenue_generated || 0);
      const spend = Number(row.ad_spend || 0);
      const clicks = Number(row.clicks || 0);
      const roiVal = row.roi_percentage != null ? Number(row.roi_percentage) : null;

      platformMetrics[platform].impressions += isFinite(views) ? views : 0;
      platformMetrics[platform].engagement += (isFinite(likes) ? likes : 0) + (isFinite(comments) ? comments : 0) + (isFinite(shares) ? shares : 0);
      platformMetrics[platform].revenue += isFinite(revenue) ? revenue : 0;
      platformMetrics[platform].spend += isFinite(spend) ? spend : 0;
      platformMetrics[platform].clicks += isFinite(clicks) ? clicks : 0;
      
      if (roiVal !== null && isFinite(roiVal)) {
        platformMetrics[platform].roi_values.push(roiVal);
      }
    });
    
    // Calculate derived metrics for each platform
    const result: ChannelData[] = Object.keys(platformMetrics).map(platform => {
      const metrics = platformMetrics[platform];
      const impressions = metrics.impressions;
      const engagement = metrics.engagement;
      const revenue = metrics.revenue;
      const spend = metrics.spend;
      const clicks = metrics.clicks;
      
      const engagement_rate = impressions > 0 ? (engagement / impressions) * 100 : 0;
      const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
      const profit = revenue - spend;
      const avg_roi = metrics.roi_values.length > 0 ? 
        metrics.roi_values.reduce((sum: number, val: number) => sum + val, 0) / metrics.roi_values.length : 0;
      const efficiency_score = impressions > 0 ? (engagement / impressions) * avg_roi : 0;
      
      return {
        platform,
        impressions,
        engagement,
        revenue,
        spend,
        total_clicks: clicks,
        avg_roi,
        profit,
        engagement_rate,
        click_through_rate: ctr,
        efficiency_score
      };
    });
    
    console.log(`📊 Channel metrics processed: ${result.length} platforms`);
    return result;
  };

  if (loading) {
    return <div className="text-center py-8">Loading channel performance...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">Error: {error}</div>;
  }

  if (!data || data.length === 0) {
    return <div className="text-center py-8 text-gray-500">No channel performance data available for the selected range</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Channel Performance</CardTitle>
        <CardDescription>
          {range === "7d" ? "Last 7 days ROI by channel" :
           range === "30d" ? "Last 30 days ROI by channel" :
           range === "90d" ? "Last 90 days ROI by channel" :
           "ROI and efficiency by marketing channel"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" strokeOpacity={0.5} />
              <XAxis 
                dataKey="platform" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  color: '#1f2937'
                }}
                formatter={(value: any) => [`${Number(value).toFixed(1)}%`, "ROI"]}
              />
              <Bar 
                dataKey="avg_roi" 
                radius={[8, 8, 0, 0]}
                stroke="#ffffff"
                strokeWidth={2}
                fill="#8b5cf6"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 text-sm text-muted-foreground text-center">
          Showing {data.length} platforms for {range}  
        </div>
      </CardContent>
    </Card>
  );
}
