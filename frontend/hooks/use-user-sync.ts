import { useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';
import { apiClient } from '@/lib/api-client';

interface UserSyncState {
  isSyncing: boolean;
  isSynced: boolean;
  error: string | null;
  user: any | null;
}

interface SyncUserResponse {
  user?: any;
  [key: string]: any;
}

export function useUserSync() {
  const { user, isSignedIn, isLoaded } = useUser();
  const [syncState, setSyncState] = useState<UserSyncState>({
    isSyncing: false,
    isSynced: false,
    error: null,
    user: null,
  });

  const syncUser = async () => {
    if (!user || !isSignedIn) return;

    setSyncState(prev => ({ ...prev, isSyncing: true, error: null }));

    try {
      // Transform Clerk user data to match backend schema expectations
      const clerkData = {
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

      const response = await apiClient.syncUserFromClerk(user.id, clerkData);

      setSyncState({
        isSyncing: false,
        isSynced: true,
        error: null,
        user: (response as SyncUserResponse).user || response,
      });
    } catch (error) {
      console.error('Failed to sync user:', error);
      setSyncState({
        isSyncing: false,
        isSynced: false,
        error: error instanceof Error ? error.message : 'Failed to sync user',
        user: null,
      });
    }
  };

  const refreshUser = async () => {
    if (!user || !isSignedIn) return;

    try {
      const response = await apiClient.getCurrentUser(user.id);
      setSyncState(prev => ({
        ...prev,
        user: response,
        isSynced: true,
        error: null,
      }));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setSyncState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to refresh user',
      }));
    }
  };

  // Auto-sync when user signs in
  useEffect(() => {
    if (isLoaded && isSignedIn && user && !syncState.isSynced && !syncState.isSyncing) {
      syncUser();
    }
  }, [isLoaded, isSignedIn, user, syncState.isSynced, syncState.isSyncing]);

  // Refresh user data when needed
  useEffect(() => {
    if (isLoaded && isSignedIn && user && syncState.isSynced) {
      refreshUser();
    }
  }, [isLoaded, isSignedIn, user]);

  return {
    ...syncState,
    syncUser,
    refreshUser,
    isAuthenticated: isSignedIn && !!user,
    clerkUser: user,
  };
}
