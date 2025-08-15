/**
 * API Client for BOS Solution Backend
 * Handles authentication headers and API communication
 */

import { useUser } from '@clerk/nextjs';

// API base URL - adjust based on your backend configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Create API headers with user authentication
 */
export function createApiHeaders(userId: string, additionalHeaders: Record<string, string> = {}) {
  return {
    'Content-Type': 'application/json',
    'X-User-ID': userId,
    ...additionalHeaders,
  };
}

/**
 * Base API client with authentication
 */
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make an authenticated API request
   */
  async request<T>(
    endpoint: string,
    options: RequestInit & { userId: string } = {} as any
  ): Promise<T> {
    const { userId, ...requestOptions } = options;
    
    if (!userId) {
      throw new Error('User ID is required for API requests');
    }

    const url = `${this.baseUrl}${endpoint}`;
    const headers = createApiHeaders(userId, requestOptions.headers as Record<string, string>);

    const response = await fetch(url, {
      ...requestOptions,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // User endpoints
  async getUserSettings(userId: string) {
    return this.request('/users/settings', { userId });
  }

  async updateUserSettings(userId: string, settings: any) {
    return this.request('/users/settings', {
      userId,
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Competitor endpoints
  async getCompetitors(userId: string) {
    return this.request('/competitors/', { userId });
  }

  async createCompetitor(userId: string, competitorData: any) {
    return this.request('/competitors/', {
      userId,
      method: 'POST',
      body: JSON.stringify(competitorData),
    });
  }

  async getCompetitor(userId: string, competitorId: string) {
    return this.request(`/competitors/${competitorId}`, { userId });
  }

  async updateCompetitor(userId: string, competitorId: string, competitorData: any) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify(competitorData),
    });
  }

  async deleteCompetitor(userId: string, competitorId: string) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'DELETE',
    });
  }

  // Monitoring endpoints
  async getMonitoringSessions(userId: string) {
    return this.request('/monitoring/sessions', { userId });
  }

  async createMonitoringSession(userId: string, sessionData: any) {
    return this.request('/monitoring/sessions', {
      userId,
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async getMonitoringAlerts(userId: string) {
    return this.request('/monitoring/alerts', { userId });
  }

  async markAlertAsRead(userId: string, alertId: string) {
    return this.request(`/monitoring/alerts/${alertId}/read`, {
      userId,
      method: 'PUT',
    });
  }

  // Dashboard AI endpoints
  async getDashboardStats(userId: string) {
    return this.request('/dashboard/stats', { userId });
  }

  async getAISuggestions(userId: string) {
    return this.request('/dashboard/ai-suggestions', { userId });
  }

  async getCompetitorGaps(userId: string) {
    return this.request('/dashboard/competitor-gaps', { userId });
  }

  async getRecentActivities(userId: string) {
    return this.request('/dashboard/recent-activities', { userId });
  }

  async getAIAnalysis(userId: string, analysisType: string = 'comprehensive') {
    return this.request('/dashboard/ai-analysis', {
      userId,
      method: 'POST',
      body: JSON.stringify({ analysis_type: analysisType }),
    });
  }

  async getCompetitiveIntelligence(userId: string) {
    return this.request('/dashboard/competitive-intelligence', { userId });
  }

  async getContentOpportunities(userId: string) {
    return this.request('/dashboard/content-opportunities', { userId });
  }

  async getEngagementForecast(userId: string) {
    return this.request('/dashboard/engagement-forecast', { userId });
  }
}

/**
 * Hook for using the API client with Clerk authentication
 */
export function useApiClient() {
  const { user, isSignedIn } = useUser();

  if (!isSignedIn || !user) {
    throw new Error('User must be signed in to use API client');
  }

  const apiClient = new ApiClient();

  return {
    apiClient,
    userId: user.id,
    isSignedIn,
  };
}

/**
 * Utility function to handle API errors
 */
export function handleApiError(error: any): string {
  if (error.message) {
    return error.message;
  }
  
  if (error.detail) {
    return error.detail;
  }
  
  return 'An unexpected error occurred';
}

// Export default instance
export const apiClient = new ApiClient();
