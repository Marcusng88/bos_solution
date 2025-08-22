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
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
    }

    // 204 No Content or empty body: return null
    if (response.status === 204) return null as T;
    const text = await response.text();
    if (!text) return null as T;
    try {
      return JSON.parse(text);
    } catch (_) {
      return text as T;
    }
  }

  // User endpoints
  async syncUserFromClerk(userId: string, clerkUserData: any) {
    return this.request('/users/sync', {
      userId,
      method: 'POST',
      body: JSON.stringify(clerkUserData),
    });
  }

  async getUserProfile(userId: string) {
    return this.request('/users/profile', { userId });
  }

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

  // User Preferences endpoints
  async saveUserPreferences(userId: string, preferences: {
    industry: string
    companySize: string
    goals: string[]
    budget: string
  }) {
    return this.request('/user-preferences', {
      userId,
      method: 'POST',
      body: JSON.stringify({
        industry: preferences.industry,
        company_size: preferences.companySize,
        marketing_goals: preferences.goals,
        monthly_budget: preferences.budget
      }),
    });
  }

  async getUserPreferences(userId: string) {
    return this.request('/user-preferences', { userId });
  }

  async updateUserPreferences(userId: string, preferences: {
    industry: string
    companySize: string
    goals: string[]
    budget: string
  }) {
    return this.request('/user-preferences', {
      userId,
      method: 'PUT',
      body: JSON.stringify({
        industry: preferences.industry,
        company_size: preferences.companySize,
        marketing_goals: preferences.goals,
        monthly_budget: preferences.budget
      }),
    });
  }

  // Competitors endpoints (consolidated from my-competitors)
  async saveCompetitor(userId: string, competitor: {
    name: string
    website: string
    platforms: string[]
    description?: string
  }) {
    return this.request('/competitors', {
      userId,
      method: 'POST',
      body: JSON.stringify({
        name: competitor.name,
        website: competitor.website,
        platforms: competitor.platforms,
        description: competitor.description
      }),
    });
  }

  async getUserCompetitors(userId: string) {
    return this.request('/competitors', { userId });
  }

  async updateCompetitor(userId: string, competitorId: string, competitor: {
    name: string
    website: string
    platforms: string[]
    description?: string
  }) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify({
        name: competitor.name,
        website: competitor.website,
        platforms: competitor.platforms,
        description: competitor.description
      }),
    });
  }

  async deleteCompetitor(userId: string, competitorId: string) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'DELETE',
    });
  }

  // Competitor endpoints (legacy - keeping for compatibility)
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
    console.log("🔍 API Client: Response.response:", (response as any)?.response)
    
    return response;
  }

  async getAIInsights(userId: string) {
    return this.request('/ai-insights/insights', { userId });
  }

  // Social Media Content Management
  async createSocialMediaAccount(userId: string, accountData: {
    platform: string;
    accountName: string;
    isTestAccount?: boolean;
  }) {
    return this.request('/social-media/accounts', {
      userId,
      method: 'POST',
      body: JSON.stringify(accountData),
    });
  }

  async getSocialMediaAccounts(userId: string, platform?: string) {
    const url = platform 
      ? `/social-media/accounts?platform=${platform}`
      : '/social-media/accounts';
    return this.request(url, { userId, method: 'GET' });
  }

  async updateSocialMediaAccount(userId: string, accountId: string, updateData: {
    accountName?: string;
    isActive?: boolean;
    isTestAccount?: boolean;
  }) {
    return this.request(`/social-media/accounts/${accountId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async deleteSocialMediaAccount(userId: string, accountId: string) {
    return this.request(`/social-media/accounts/${accountId}`, {
      userId,
      method: 'DELETE',
    });
  }

  async createContentUpload(userId: string, uploadData: {
    title?: string;
    contentText: string;
    mediaFiles?: Array<{
      url: string;
      type: string;
      size?: number;
      filename?: string;
      mimeType?: string;
    }>;
    scheduledAt?: string;
    platform: string;
    accountId: string;
    isTestPost?: boolean;
  }) {
    return this.request('/social-media/uploads', {
      userId,
      method: 'POST',
      body: JSON.stringify(uploadData),
    });
  }

  async getContentUploads(userId: string, status?: string) {
    const url = status 
      ? `/social-media/uploads?status=${status}`
      : '/social-media/uploads';
    return this.request(url, { userId, method: 'GET' });
  }

  async updateContentUpload(userId: string, uploadId: string, updateData: {
    title?: string;
    contentText?: string;
    mediaFiles?: Array<{
      url: string;
      type: string;
      size?: number;
      filename?: string;
      mimeType?: string;
    }>;
    scheduledAt?: string;
    status?: string;
    isTestPost?: boolean;
  }) {
    return this.request(`/social-media/uploads/${uploadId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async deleteContentUpload(userId: string, uploadId: string) {
    return this.request(`/social-media/uploads/${uploadId}`, {
      userId,
      method: 'DELETE',
    });
  }

  async postContentNow(userId: string, uploadId: string) {
    return this.request(`/social-media/uploads/${uploadId}/post`, {
      userId,
      method: 'POST',
    });
  }

  async createContentTemplate(userId: string, templateData: {
    name: string;
    description?: string;
    contentText: string;
    mediaFiles?: Array<{
      url: string;
      type: string;
      size?: number;
      filename?: string;
      mimeType?: string;
    }>;
    platforms: string[];
    tags?: string[];
    isActive?: boolean;
  }) {
    return this.request('/social-media/templates', {
      userId,
      method: 'POST',
      body: JSON.stringify(templateData),
    });
  }

  async getContentTemplates(userId: string, platform?: string) {
    const url = platform 
      ? `/social-media/templates?platform=${platform}`
      : '/social-media/templates';
    return this.request(url, { userId, method: 'GET' });
  }

  async updateContentTemplate(userId: string, templateId: string, updateData: {
    name?: string;
    description?: string;
    contentText?: string;
    mediaFiles?: Array<{
      url: string;
      type: string;
      size?: number;
      filename?: string;
      mimeType?: string;
    }>;
    platforms?: string[];
    tags?: string[];
    isActive?: boolean;
  }) {
    return this.request(`/social-media/templates/${templateId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async deleteContentTemplate(userId: string, templateId: string) {
    return this.request(`/social-media/templates/${templateId}`, {
      userId,
      method: 'DELETE',
    });
  }

  async previewContent(userId: string, contentText: string, platform: string, mediaCount: number = 0) {
    const formData = new FormData();
    formData.append('content_text', contentText);
    formData.append('platform', platform);
    formData.append('media_count', mediaCount.toString());

    return this.request('/social-media/preview', {
      userId,
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }

  async bulkUploadContent(userId: string, bulkRequest: {
    content: {
      title?: string;
      contentText: string;
      mediaFiles?: Array<{
        url: string;
        type: string;
        size?: number;
        filename?: string;
        mimeType?: string;
      }>;
      scheduledAt?: string;
      platform: string;
      accountId: string;
      isTestPost?: boolean;
    };
    platforms: string[];
    scheduleStrategy?: string;
    customSchedule?: Record<string, string>;
  }) {
    return this.request('/social-media/bulk-upload', {
      userId,
      method: 'POST',
      body: JSON.stringify(bulkRequest),
    });
  }

  async getPlatformStatus(userId: string) {
    return this.request('/social-media/platform-status', {
      userId,
      method: 'GET',
    });
  }

  async getConnectedAccounts(userId: string) {
    return this.request('/social-media/connected-accounts', {
      userId,
      method: 'GET',
    });
  }

  async connectPlatform(userId: string, platform: string) {
    return this.request(`/social-media/connect/${platform}`, {
      userId,
      method: 'POST',
      body: JSON.stringify({}),
      headers: {
        'Content-Type': 'application/json',
      },
    });
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
