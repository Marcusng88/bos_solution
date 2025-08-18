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

  // Self-optimization endpoints
  async getDashboardMetrics(userId: string) {
    return this.request('/self-optimization/dashboard/metrics', { userId });
  }

  async getDetailedDashboardMetrics(userId: string) {
    return this.request('/self-optimization/dashboard/metrics/detailed', { userId });
  }

  async getCampaigns(userId: string, params?: {
    limit?: number;
    offset?: number;
    ongoing_only?: boolean;
  }) {
    const queryString = params ? '?' + new URLSearchParams(
      Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined) acc[key] = String(value);
        return acc;
      }, {} as Record<string, string>)
    ).toString() : '';
    
    return this.request(`/self-optimization/campaigns${queryString}`, { userId });
  }

  async getOverspendingPredictions(userId: string) {
    return this.request('/self-optimization/overspending-predictions', { userId });
  }

  async updateCampaignStatus(userId: string, campaignName: string, status: string) {
    return this.request('/self-optimization/campaigns/status', {
      userId,
      method: 'PUT',
      body: JSON.stringify({ campaign_name: campaignName, ongoing: status }),
    });
  }

  async updateCampaignBudget(userId: string, campaignName: string, newBudget: number) {
    return this.request('/self-optimization/campaigns/budget', {
      userId,
      method: 'PUT',
      body: JSON.stringify({ campaign_name: campaignName, budget: newBudget }),
    });
  }

  async createCampaign(userId: string, campaignData: any) {
    return this.request('/self-optimization/campaigns', {
      userId,
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  }

  async getCampaignStats(userId: string, days: number = 30) {
    return this.request(`/self-optimization/campaigns/stats?days=${days}`, { userId });
  }

  async getCampaignPerformance(userId: string, campaignName: string, days: number = 30) {
    return this.request(`/self-optimization/campaigns/${encodeURIComponent(campaignName)}/performance?days=${days}`, { userId });
  }

  async getBudgetMonitoring(userId: string, days: number = 7) {
    return this.request(`/self-optimization/budget/monitoring?days=${days}`, { userId });
  }

  async getOptimizationAlerts(userId: string, unreadOnly: boolean = false, limit: number = 50) {
    return this.request(`/self-optimization/alerts?unread_only=${unreadOnly}&limit=${limit}`, { userId });
  }

  async markOptimizationAlertAsRead(userId: string, alertId: string) {
    return this.request(`/self-optimization/alerts/${alertId}/read`, {
      userId,
      method: 'PUT',
    });
  }

  async getRiskPatterns(userId: string, unresolvedOnly: boolean = false, limit: number = 50) {
    return this.request(`/self-optimization/risk-patterns?unresolved_only=${unresolvedOnly}&limit=${limit}`, { userId });
  }

  async getOptimizationRecommendations(userId: string, unappliedOnly: boolean = false, limit: number = 50) {
    return this.request(`/self-optimization/recommendations?unapplied_only=${unappliedOnly}&limit=${limit}`, { userId });
  }

  async applyRecommendation(userId: string, recommendationId: string) {
    return this.request(`/self-optimization/recommendations/${recommendationId}/apply`, {
      userId,
      method: 'PUT',
    });
  }

  async triggerOptimizationAnalysis(userId: string) {
    return this.request('/self-optimization/analyze', {
      userId,
      method: 'POST',
    });
  }

  async aiChatAssistant(userId: string, message: string) {
    return this.request('/self-optimization/ai-chat', {
      userId,
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // AI Insights endpoints
  async analyzeCampaigns(userId: string, options?: {
    include_competitors?: boolean;
    include_monitoring?: boolean;
    analysis_type?: string;
  }) {
    return this.request('/ai-insights/analyze', {
      userId,
      method: 'POST',
      body: JSON.stringify(options || {}),
    });
  }

  async chatWithAI(userId: string, message: string) {
    console.log("🔍 API Client: Making chat request to /ai-insights/chat")
    console.log("🔍 API Client: User ID:", userId)
    console.log("🔍 API Client: Message:", message)
    
    const response = await this.request('/ai-insights/chat', {
      userId,
      method: 'POST',
      body: JSON.stringify({ message }),
    });
    
    console.log("🔍 API Client: Raw response received:", response)
    console.log("🔍 API Client: Response type:", typeof response)
    console.log("🔍 API Client: Response.response:", response.response)
    
    return response;
  }

  async getAIInsights(userId: string) {
    return this.request('/ai-insights/insights', { userId });
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
