import { apiClient } from './api-client';

export interface Draft {
  id: string;
  user_id: string;
  title: string;
  content: string;
  platform: string;
  content_type: string;
  status: string;
  source_id?: string;
  hashtags: string[];
  media_urls: string[];
  scheduling_options: Record<string, any>;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateDraftData {
  title: string;
  content: string;
  platform: string;
  content_type: string;
  status?: string;
  source_id?: string;
  hashtags?: string[];
  media_urls?: string[];
  scheduling_options?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface UpdateDraftData {
  title?: string;
  content?: string;
  platform?: string;
  content_type?: string;
  status?: string;
  hashtags?: string[];
  media_urls?: string[];
  scheduling_options?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface DraftListResponse {
  drafts: Draft[];
  total: number;
  page: number;
  per_page: number;
}

export class DraftService {
  private static instance: DraftService;
  
  private constructor() {}

  static getInstance(): DraftService {
    if (!DraftService.instance) {
      DraftService.instance = new DraftService();
    }
    return DraftService.instance;
  }

  /**
   * Create a new draft
   */
  async createDraft(data: CreateDraftData, userId: string): Promise<Draft> {
    try {
      console.log('📝 Creating draft:', data);
      const response = await apiClient.request<Draft>('/drafts', {
        userId,
        method: 'POST',
        body: JSON.stringify(data),
      });
      console.log('✅ Draft created:', response);
      return response;
    } catch (error) {
      console.error('❌ Error creating draft:', error);
      throw new Error('Failed to create draft');
    }
  }

  /**
   * Get all drafts for the current user
   */
  async getDrafts(
    userId: string,
    status?: string,
    page: number = 1,
    perPage: number = 20
  ): Promise<DraftListResponse> {
    try {
      console.log('📚 Getting drafts:', { status, page, perPage });
      
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
      });
      
      if (status) {
        params.append('status', status);
      }

      const response = await apiClient.request<DraftListResponse>(`/drafts?${params.toString()}`, {
        userId,
        method: 'GET',
      });
      console.log('✅ Got drafts:', response);
      return response;
    } catch (error) {
      console.error('❌ Error getting drafts:', error);
      throw new Error('Failed to get drafts');
    }
  }

  /**
   * Get a specific draft by ID
   */
  async getDraftById(draftId: string, userId: string): Promise<Draft> {
    try {
      console.log('📖 Getting draft by ID:', draftId);
      const response = await apiClient.request<Draft>(`/drafts/${draftId}`, {
        userId,
        method: 'GET',
      });
      console.log('✅ Got draft:', response);
      return response;
    } catch (error) {
      console.error('❌ Error getting draft by ID:', error);
      throw new Error('Failed to get draft');
    }
  }

  /**
   * Update a draft
   */
  async updateDraft(draftId: string, data: UpdateDraftData, userId: string): Promise<Draft> {
    try {
      console.log('📝 Updating draft:', draftId, data);
      const response = await apiClient.request<Draft>(`/drafts/${draftId}`, {
        userId,
        method: 'PUT',
        body: JSON.stringify(data),
      });
      console.log('✅ Draft updated:', response);
      return response;
    } catch (error) {
      console.error('❌ Error updating draft:', error);
      throw new Error('Failed to update draft');
    }
  }

  /**
   * Delete a draft
   */
  async deleteDraft(draftId: string, userId: string): Promise<void> {
    try {
      console.log('🗑️ Deleting draft:', draftId);
      await apiClient.request(`/drafts/${draftId}`, {
        userId,
        method: 'DELETE',
      });
      console.log('✅ Draft deleted');
    } catch (error) {
      console.error('❌ Error deleting draft:', error);
      throw new Error('Failed to delete draft');
    }
  }

  /**
   * Get draft by source ID (from content planning)
   */
  async getDraftBySourceId(sourceId: string, userId: string): Promise<Draft> {
    try {
      console.log('🔍 Getting draft by source ID:', sourceId);
      const response = await apiClient.request<Draft>(`/drafts/by-source/${sourceId}`, {
        userId,
        method: 'GET',
      });
      console.log('✅ Got draft by source:', response);
      return response;
    } catch (error) {
      console.error('❌ Error getting draft by source ID:', error);
      throw new Error('Failed to get draft by source ID');
    }
  }

  /**
   * Create draft from content planning approval
   */
  async createDraftFromContentPlanning(data: CreateDraftData, userId: string): Promise<Draft> {
    try {
      console.log('📋 Creating draft from content planning:', data);
      const response = await apiClient.request<Draft>('/drafts/from-content-planning', {
        userId,
        method: 'POST',
        body: JSON.stringify(data),
      });
      console.log('✅ Draft created from content planning:', response);
      return response;
    } catch (error) {
      console.error('❌ Error creating draft from content planning:', error);
      throw new Error('Failed to create draft from content planning');
    }
  }

  /**
   * Save draft content (create or update based on existence)
   */
  async saveDraft(data: CreateDraftData, userId: string, draftId?: string): Promise<Draft> {
    if (draftId) {
      return this.updateDraft(draftId, data, userId);
    } else {
      return this.createDraft(data, userId);
    }
  }

  /**
   * Auto-save draft (throttled save for real-time editing)
   */
  private saveTimeouts = new Map<string, NodeJS.Timeout>();

  autoSaveDraft(data: CreateDraftData, userId: string, draftId?: string, delay: number = 2000): Promise<Draft> {
    const key = draftId || 'new-draft';
    
    // Clear existing timeout
    const existingTimeout = this.saveTimeouts.get(key);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(async () => {
        try {
          const result = await this.saveDraft(data, userId, draftId);
          this.saveTimeouts.delete(key);
          resolve(result);
        } catch (error) {
          this.saveTimeouts.delete(key);
          reject(error);
        }
      }, delay);
      
      this.saveTimeouts.set(key, timeout);
    });
  }

  /**
   * Cancel auto-save
   */
  cancelAutoSave(draftId?: string): void {
    const key = draftId || 'new-draft';
    const timeout = this.saveTimeouts.get(key);
    if (timeout) {
      clearTimeout(timeout);
      this.saveTimeouts.delete(key);
    }
  }
}

// Export singleton instance
export const draftService = DraftService.getInstance();