/**
 * API Client for BOS Solution Backend
 * Handles authentication headers and API communication
 */

import { useUser } from '@clerk/nextjs';
import { Competitor, CompetitorCreate, CompetitorUpdate, CompetitorStats } from './types';
import { useMemo } from 'react';

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
 * Get authentication headers for API requests
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  // Get the current user from Clerk
  const { useUser } = await import('@clerk/nextjs');
  
  // Since this is a utility function, we need to get the user ID differently
  // For now, we'll use a more realistic approach
  try {
    // Try to get user ID from localStorage or session storage if available
    const storedUserId = typeof window !== 'undefined' ? 
      localStorage.getItem('clerk_user_id') || 
      sessionStorage.getItem('clerk_user_id') : null;
    
    if (storedUserId) {
      return {
        'Content-Type': 'application/json',
        'X-User-ID': storedUserId,
      };
    }
    
    // Fallback to mock ID for development/testing
    console.warn('No user ID found, using mock ID for development');
    return {
      'Content-Type': 'application/json',
      'X-User-ID': 'user_test123456789', // Mock Clerk user ID format for testing
    };
  } catch (error) {
    console.error('Error getting auth headers:', error);
    // Fallback to mock ID
    return {
      'Content-Type': 'application/json',
      'X-User-ID': 'user_test123456789', // Mock Clerk user ID format for testing
    };
  }
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

    console.log(`🌐 API Request: ${url}`);
    console.log(`🔑 Headers:`, headers);

    const response = await fetch(url, {
      ...requestOptions,
      headers,
    });

    console.log(`📡 Response: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      
      // Try to parse error body as JSON; if not JSON, fall back to text
      let message = `API request failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData?.detail) message = errorData.detail;
      } catch (_) {
        try {
          const text = await response.text();
          if (text) message = text;
        } catch (_) {}
      }
      throw new Error(message);
    }

    // 204 No Content or empty body: return null
    if (response.status === 204) return null as unknown as T;
    const text = await response.text();
    if (!text) return null as unknown as T;
    try {
      return JSON.parse(text) as T;
    } catch (_) {
      // If backend returned non-JSON (shouldn't happen), return as any
      return text as unknown as T;
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

  async updateUserProfile(
    userId: string,
    profileData: {
      email?: string;
      firstName?: string;
      lastName?: string;
      profileImageUrl?: string;
    }
  ): Promise<any> {
    return this.request(`/auth/profile`, {
      userId,
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  /**
   * Update user onboarding completion status
   */
  async updateUserOnboardingStatus(userId: string, isComplete: boolean): Promise<any> {
    return this.request(`/users/${userId}/onboarding-status`, {
      method: 'PATCH',
      userId,
      body: JSON.stringify({ onboarding_complete: isComplete }),
    });
  }

  /**
   * Get user onboarding completion status
   */
  async getUserOnboardingStatus(userId: string): Promise<any> {
    return this.request(`/users/${userId}/onboarding-status`, {
      method: 'GET',
      userId,
    });
  }

  /**
   * Save user preferences to database
   */
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

  // Competitor endpoints
  async saveCompetitor(userId: string, competitor: {
    name: string
    website: string
    platforms: string[]
  }) {
    return this.request('/competitors', {
      userId,
      method: 'POST',
      body: JSON.stringify({
        name: competitor.name,
        website_url: competitor.website, // Backend expects website_url
        platforms: competitor.platforms
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
  }) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'PUT',
      body: JSON.stringify({
        name: competitor.name,
        website_url: competitor.website, // Backend expects website_url
        platforms: competitor.platforms
      }),
    });
  }

  async deleteCompetitor(userId: string, competitorId: string) {
    return this.request(`/competitors/${competitorId}`, {
      userId,
      method: 'DELETE',
    });
  }

  // Legacy competitor methods - keeping for compatibility but marked as deprecated
  async getCompetitors(userId: string) {
    console.warn('getCompetitors is deprecated, use getUserCompetitors instead');
    return this.getUserCompetitors(userId);
  }

  async createCompetitor(userId: string, competitorData: any) {
    console.warn('createCompetitor is deprecated, use saveCompetitor instead');
    return this.saveCompetitor(userId, competitorData);
  }

  async getCompetitor(userId: string, competitorId: string) {
    return this.request(`/competitors/${competitorId}`, { userId });
  }

  // Note: updateCompetitor and deleteCompetitor are handled by the my-competitors endpoints above

  // Monitoring endpoints
  async getMonitoringSettings(userId: string) {
    return this.request('/monitoring/settings', { userId });
  }

  async updateMonitoringSettings(userId: string, settings: any) {
    return this.request('/monitoring/settings', {
      userId,
      method: 'PUT',
      body: JSON.stringify(settings),
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

  // Additional monitoring methods for continuous monitoring dashboard
  async getMonitoringStatus(userId: string) {
    return this.request('/monitoring/status', { userId });
  }

  async getMonitoringStats(userId: string) {
    return this.request('/monitoring/stats', { userId });
  }

  async startContinuousMonitoring(userId: string) {
    return this.request('/monitoring/start', {
      userId,
      method: 'POST',
    });
  }

  async stopContinuousMonitoring(userId: string) {
    return this.request('/monitoring/stop', {
      userId,
      method: 'POST',
    });
  }

  async runMonitoringForAllCompetitors(userId: string) {
    return this.request('/monitoring/scan-all', {
      userId,
      method: 'POST',
    });
  }

  // User sync methods
  async getCurrentUser(userId: string) {
    return this.request('/users/profile', { userId });
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

  // Memoize the API client instance to prevent recreation on every render
  const apiClient = useMemo(() => new ApiClient(), []);

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

// Competitor API methods
export const competitorAPI = {
  // Get all competitors
  getCompetitors: async (userId: string): Promise<Competitor[]> => {
    const response = await fetch(`${API_BASE_URL}/competitors/`, {
      headers: createApiHeaders(userId),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch competitors');
    }
    
    return response.json();
  },

  // Create a new competitor
  createCompetitor: async (competitorData: CompetitorCreate, userId: string): Promise<Competitor> => {
    try {
      console.log('Creating competitor with data:', competitorData);
      console.log('User ID:', userId);
      console.log('API URL:', `${API_BASE_URL}/competitors/`);
      console.log('Headers:', createApiHeaders(userId));
      
      if (!userId || userId.trim() === '') {
        throw new Error('User ID is required');
      }
      
      const response = await fetch(`${API_BASE_URL}/competitors/`, {
        method: 'POST',
        headers: createApiHeaders(userId),
        body: JSON.stringify(competitorData),
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        
        let errorMessage = 'Failed to create competitor';
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          errorMessage = `${errorMessage}: ${response.status} ${response.statusText}`;
        }
        
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      console.log('Success response:', result);
      return result;
    } catch (error) {
      console.error('Error in createCompetitor:', error);
      
      // Provide more specific error messages
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error: Unable to connect to the server. Please check your internet connection and try again.');
      }
      
      throw error;
    }
  },

  // Update a competitor
  updateCompetitor: async (id: string, competitorData: Partial<CompetitorCreate>, userId: string): Promise<Competitor> => {
    const response = await fetch(`${API_BASE_URL}/competitors/${id}`, {
      method: 'PUT',
      headers: createApiHeaders(userId),
      body: JSON.stringify(competitorData),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update competitor');
    }
    
    return response.json();
  },

  // Delete a competitor
  deleteCompetitor: async (id: string, userId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/competitors/${id}`, {
      method: 'DELETE',
      headers: createApiHeaders(userId),
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete competitor');
    }
  },

  // Get competitor statistics
  getCompetitorStats: async (userId: string): Promise<CompetitorStats> => {
    const response = await fetch(`${API_BASE_URL}/competitors/stats/summary`, {
      headers: createApiHeaders(userId),
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch competitor statistics');
    }
    
    return response.json();
  },

  // Toggle competitor status
  toggleCompetitorStatus: async (id: string, userId: string): Promise<Competitor> => {
    const response = await fetch(`${API_BASE_URL}/competitors/${id}/toggle-status`, {
      method: 'POST',
      headers: createApiHeaders(userId),
    });
    
    if (!response.ok) {
      throw new Error('Failed to toggle competitor status');
    }
    
    return response.json();
  },

  // Update scan frequency
  updateScanFrequency: async (id: string, frequencyMinutes: number, userId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/competitors/${id}/scan-frequency`, {
      method: 'PUT',
      headers: createApiHeaders(userId),
      body: JSON.stringify({ frequency_minutes: frequencyMinutes }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update scan frequency');
    }
  },

  // Scan all competitors
  scanAllCompetitors: async (userId: string): Promise<any> => {
    console.log('🔍 scanAllCompetitors called with userId:', userId);
    console.log('🔍 API_BASE_URL:', API_BASE_URL);
    console.log('🔍 Full URL:', `${API_BASE_URL}/competitors/scan-all`);
    
    const headers = createApiHeaders(userId);
    console.log('🔍 Request headers:', headers);
    
    try {
      console.log('🔍 Making POST request to:', `${API_BASE_URL}/competitors/scan-all`);
      
      const response = await fetch(`${API_BASE_URL}/competitors/scan-all`, {
        method: 'POST',
        headers: headers,
      });
      
      console.log('🔍 Response status:', response.status);
      console.log('🔍 Response headers:', response.headers);
      console.log('🔍 Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 Error response text:', errorText);
        throw new Error(`Failed to scan all competitors: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('🔍 Success response:', result);
      return result;
    } catch (error) {
      console.error('🔍 Error in scanAllCompetitors:', error);
      throw error;
    }
  },
};

// Monitoring API
export const monitoringAPI = {
  // Get monitoring data
  getMonitoringData: async (
    userId: string, 
    filters?: {
      competitorId?: string;
      platform?: string;
      limit?: number;
    }
  ): Promise<any> => {
    const searchParams = new URLSearchParams();
    if (filters?.competitorId) searchParams.append('competitor_id', filters.competitorId);
    if (filters?.platform) searchParams.append('platform', filters.platform);
    if (filters?.limit) searchParams.append('limit', filters.limit.toString());
    
    const url = `${API_BASE_URL}/monitoring/monitoring-data${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    
    console.log(`🌐 Monitoring API Request: ${url}`);
    console.log(`🔑 Monitoring API Headers:`, createApiHeaders(userId));
    
    const response = await fetch(url, {
      headers: createApiHeaders(userId),
    });
    
    console.log(`📡 Monitoring API Response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch monitoring data');
    }

    const responseData = await response.json();
    console.log(`✅ Monitoring API Response data:`, responseData);
    return responseData;
  },

  // Get monitoring stats
  getMonitoringStats: async (userId: string): Promise<any> => {
    const url = `${API_BASE_URL}/monitoring/monitoring-stats`;
    
    console.log(`🌐 Monitoring Stats API Request: ${url}`);
    console.log(`🔑 Monitoring Stats API Headers:`, createApiHeaders(userId));
    
    const response = await fetch(url, {
      headers: createApiHeaders(userId),
    });
    
    console.log(`📡 Monitoring Stats API Response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch monitoring stats');
    }

    const responseData = await response.json();
    console.log(`✅ Monitoring Stats API Response data:`, responseData);
    return responseData;
  },

  // Scan specific platform for a competitor
  scanPlatform: async (userId: string, platform: string, competitorId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/monitoring/scan-platform/${platform}`, {
      method: 'POST',
      headers: createApiHeaders(userId),
      body: JSON.stringify({ competitor_id: competitorId }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to scan ${platform} for competitor`);
    }
    
    return response.json();
  },

  // Scan specific competitor with optional platforms
  scanCompetitor: async (userId: string, competitorId: string, platforms?: string[]): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/monitoring/scan-competitor/${competitorId}`, {
      method: 'POST',
      headers: createApiHeaders(userId),
      body: JSON.stringify({ platforms }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to scan competitor');
    }
    
    return response.json();
  },
};