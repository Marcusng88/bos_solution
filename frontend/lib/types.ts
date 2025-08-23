/**
 * Type definitions for BOS Solution
 */

export interface Competitor {
  id: string;
  name: string;
  description?: string;
  website_url?: string;
  social_media_handles?: Record<string, string>;
  industry?: string;
  status: 'active' | 'paused' | 'error';
  created_at: string;
  updated_at: string;
  last_scan_at?: string;
  scan_frequency_minutes: number;
  user_id: string;  // This will be converted from UUID to string by the API
}

export interface CompetitorCreate {
  name: string;
  description?: string;
  website_url?: string;
  social_media_handles?: Record<string, string>;
  industry?: string;
  scan_frequency_minutes?: number;
}

export interface CompetitorUpdate {
  name?: string;
  description?: string;
  website_url?: string;
  social_media_handles?: Record<string, string>;
  industry?: string;
  status?: 'active' | 'paused' | 'error';
  scan_frequency_minutes?: number;
}

export interface CompetitorStats {
  total_competitors: number;
  active_competitors: number;
  paused_competitors: number;
  error_competitors: number;
  recent_scans_24h: number;
}

export interface Platform {
  id: string;
  name: string;
  icon: string;
  description: string;
}

export interface MonitoringData {
  id: string;
  competitor_id: string;
  platform: string;
  post_id?: string;
  content_text?: string;
  content_hash: string;
  engagement_metrics?: Record<string, any>;
  detected_at: string;
  is_content_change: boolean;
  previous_content_hash?: string;
}

export interface MonitoringAlert {
  id: string;
  user_id: string;
  competitor_id: string;
  monitoring_data_id?: string;
  alert_type: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  is_read: boolean;
  alert_metadata?: Record<string, any>;
  created_at: string;
}
