/**
 * Custom hook to sync Clerk user data with backend database
 */

import { useUser } from '@clerk/nextjs';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api-client';

interface SyncState {
  isLoading: boolean;
  isError: boolean;
  error?: string;
  isSynced: boolean;
}

export function useUserSync() {
  const { user, isSignedIn } = useUser();
  const [syncState, setSyncState] = useState<SyncState>({
    isLoading: false,
    isError: false,
    isSynced: false,
  });

  const syncUser = async () => {
    if (!user || !isSignedIn) {
      return;
    }

    setSyncState(prev => ({ ...prev, isLoading: true, isError: false }));

    try {
      // Transform Clerk user data to match our schema
      const clerkUserData = {
        id: user.id,
        email_addresses: user.emailAddresses.map(email => ({
          id: email.id,
          email_address: email.emailAddress,
        })),
        first_name: user.firstName,
        last_name: user.lastName,
        image_url: user.imageUrl,
        primary_email_address_id: user.primaryEmailAddressId,
      };

      await apiClient.syncUserFromClerk(user.id, clerkUserData);

      setSyncState(prev => ({
        ...prev,
        isLoading: false,
        isSynced: true,
      }));
    } catch (error: any) {
      setSyncState(prev => ({
        ...prev,
        isLoading: false,
        isError: true,
        error: error.message || 'Failed to sync user data',
      }));
    }
  };

  // Auto-sync when user signs in
  useEffect(() => {
    if (isSignedIn && user && !syncState.isSynced && !syncState.isLoading) {
      syncUser();
    }
  }, [isSignedIn, user, syncState.isSynced, syncState.isLoading]);

  return {
    ...syncState,
    syncUser,
  };
}

// Types for user data
export interface UserProfile {
  id: string;
  clerk_id: string;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  profile_image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSettings {
  id: string;
  user_id: string;
  global_monitoring_enabled: boolean;
  default_scan_frequency_minutes: number;
  alert_preferences: {
    email_alerts: boolean;
    push_notifications: boolean;
    new_posts: boolean;
    content_changes: boolean;
    engagement_spikes: boolean;
    sentiment_changes: boolean;
  };
  notification_schedule: {
    quiet_hours_start: string;
    quiet_hours_end: string;
    timezone: string;
  };
  created_at: string;
  updated_at: string;
}
