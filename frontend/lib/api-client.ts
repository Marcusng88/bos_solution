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

  // My Competitors endpoints
  async saveCompetitor(userId: string, competitor: {
    name: string
    website: string
    platforms: string[]
  }) {
    return this.request('/my-competitors', {
      userId,
      method: 'POST',
      body: JSON.stringify({
        competitor_name: competitor.name,
        website_url: competitor.website,
        active_platforms: competitor.platforms
      }),
    });
  }

  async getUserCompetitors(userId: string) {
    return this.request('/my-competitors', { userId });
  }

  async updateCompetitor(userId: string, competitorId: string, competitor: {
    name: string
    website: string
    platforms: string[]
  }) {
    return this.request(`/my-competitors/${competitorId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify({
        competitor_name: competitor.name,
        website_url: competitor.website,
        active_platforms: competitor.platforms
      }),
    });
  }

  async deleteCompetitor(userId: string, competitorId: string) {
    return this.request(`/my-competitors/${competitorId}`, {
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

  // Note: updateCompetitor and deleteCompetitor are handled by the my-competitors endpoints above

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
