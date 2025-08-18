import { useEffect, useState } from 'react';
import { useUser } from '@clerk/nextjs';
import { apiClient } from '@/lib/api-client';

interface UserSyncState {
  isSyncing: boolean;
  isSynced: boolean;
  error: string | null;
  user: any | null;
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
      const response = await apiClient.syncUserWithClerk({
        userId: user.id,
        email: user.emailAddresses[0]?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        profileImageUrl: user.imageUrl,
      });

      setSyncState({
        isSyncing: false,
        isSynced: true,
        error: null,
        user: response.user || response,
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
