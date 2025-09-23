import { useEffect, useState, useRef, useCallback } from 'react';
import { useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

interface UserSyncState {
  isSyncing: boolean;
  isSynced: boolean;
  error: string | null;
  user: any | null;
  redirectPath: string | null;
}

interface SyncUserResponse {
  user?: any;
  [key: string]: any;
}

interface UserStatusResponse {
  exists: boolean;
  redirect_to: string;
  user: any;
  message: string;
  onboarding_complete?: boolean;
}

export function useUserSync() {
  const { user, isSignedIn, isLoaded } = useUser();
  const router = useRouter();
  const [syncState, setSyncState] = useState<UserSyncState>({
    isSyncing: false,
    isSynced: false,
    error: null,
    user: null,
    redirectPath: null,
  });
  const [retryCount, setRetryCount] = useState(0);
  const MAX_RETRIES = 3;
  const hasCheckedStatus = useRef(false);

  const checkUserStatus = useCallback(async () => {
    if (!user || !isSignedIn || hasCheckedStatus.current) return;
    
    hasCheckedStatus.current = true;
    
    try {
      console.log('🔍 Checking user status...');
      console.log('👤 User ID:', user.id);
      console.log('📧 User email:', user.emailAddresses?.[0]?.emailAddress);
      
      const response = await apiClient.checkUserStatus(user.id);
      const statusData = response as UserStatusResponse;
      
      console.log('✅ User status response:', statusData);
      console.log('🎯 Redirect path:', statusData.redirect_to);
      console.log('✅ Onboarding complete:', statusData.onboarding_complete);
      
      if (statusData.exists) {
        // User exists - check if they should go to dashboard or onboarding
        if (statusData.onboarding_complete) {
          // User has completed onboarding - they can go to dashboard
          console.log('🚀 User exists and onboarding complete, redirecting to dashboard');
          setSyncState({
            isSyncing: false,
            isSynced: true,
            error: null,
            user: statusData.user,
            redirectPath: 'dashboard',
          });
          
          // Only redirect if not already on dashboard, dashboard sub-route, or welcome page
          if (!window.location.pathname.startsWith('/dashboard') && !window.location.pathname.startsWith('/welcome')) {
            console.log('🔄 Redirecting to dashboard...');
            router.push('/dashboard');
          }
        } else {
          // User exists but hasn't completed onboarding
          console.log('📝 User exists but onboarding incomplete, redirecting to onboarding');
          setSyncState({
            isSyncing: false,
            isSynced: true,
            error: null,
            user: statusData.user,
            redirectPath: 'onboarding',
          });
          
          // Only redirect if not already on onboarding, onboarding sub-route, or welcome page
          if (!window.location.pathname.startsWith('/onboarding') && !window.location.pathname.startsWith('/welcome')) {
            console.log('🔄 Redirecting to onboarding...');
            router.push('/onboarding');
          }
        }
      } else {
        // User doesn't exist - they need onboarding
        console.log('🆕 New user, redirecting to onboarding');
        setSyncState({
          isSyncing: false,
          isSynced: true, // Mark as synced to prevent infinite loading
          error: null,
          user: null,
          redirectPath: statusData.redirect_to,
        });
        
        // Only redirect if not already on onboarding, onboarding sub-route, or welcome page
        if (!window.location.pathname.startsWith('/onboarding') && !window.location.pathname.startsWith('/welcome')) {
          console.log('🔄 Redirecting to onboarding...');
          router.push('/onboarding');
        }
      }
    } catch (error) {
      console.error('❌ Failed to check user status:', error);
      // If check fails, mark as synced to prevent infinite loading
      setSyncState({
        isSyncing: false,
        isSynced: true,
        error: 'Failed to check user status. Please try again.',
        user: null,
        redirectPath: 'onboarding', // Default to onboarding on error
      });
    }
  }, [user, isSignedIn, router]);

  const syncUser = useCallback(async () => {
    if (!user || !isSignedIn) return;

    setSyncState(prev => ({ ...prev, isSyncing: true, error: null }));

    try {
      console.log('🔄 Syncing user...');
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
      console.log('✅ User sync response:', response);

      setSyncState({
        isSyncing: false,
        isSynced: true,
        error: null,
        user: (response as SyncUserResponse).user || response,
        redirectPath: 'onboarding',
      });
      
      // Only redirect to onboarding if not already there or on welcome page
      if (!window.location.pathname.startsWith('/onboarding') && !window.location.pathname.startsWith('/welcome')) {
        router.push('/onboarding');
      }
    } catch (error) {
      console.error('❌ Failed to sync user:', error);
      setSyncState({
        isSyncing: false,
        isSynced: true, // Mark as synced to prevent infinite loading
        error: error instanceof Error ? error.message : 'Failed to sync user',
        user: null,
        redirectPath: 'onboarding',
      });
    }
  }, [user, isSignedIn, router]);

  // Auto-check user status when user signs in (only once)
  useEffect(() => {
    if (isLoaded && isSignedIn && user && !hasCheckedStatus.current) {
      console.log('🚀 User signed in, checking status...');
      checkUserStatus();
    }
  }, [isLoaded, isSignedIn, user, checkUserStatus]);

  // Fallback: if sync takes too long, mark as synced
  useEffect(() => {
    if (isLoaded && isSignedIn && user && !syncState.isSynced && !syncState.isSyncing) {
      const timeout = setTimeout(() => {
        console.warn('⚠️ User sync timeout, forcing completion to prevent infinite loading');
        setSyncState(prev => ({
          ...prev,
          isSynced: true,
          redirectPath: 'onboarding',
        }));
      }, 5000); // 5 second timeout
      
      return () => clearTimeout(timeout);
    }
  }, [isLoaded, isSignedIn, user, syncState.isSynced, syncState.isSyncing]);

  const refreshUser = useCallback(async () => {
    if (!user || !isSignedIn) return;
    // Reset the check flag to allow re-checking
    hasCheckedStatus.current = false;
    await checkUserStatus();
  }, [user, isSignedIn, checkUserStatus]);

  const retrySync = useCallback(() => {
    if (retryCount < MAX_RETRIES) {
      setRetryCount(prev => prev + 1);
      hasCheckedStatus.current = false; // Reset to allow re-checking
      checkUserStatus();
    }
  }, [retryCount, checkUserStatus]);

  return {
    ...syncState,
    syncUser,
    refreshUser,
    retrySync,
    retryCount,
    maxRetries: MAX_RETRIES,
    isAuthenticated: isSignedIn && !!user,
    clerkUser: user,
  };
}
