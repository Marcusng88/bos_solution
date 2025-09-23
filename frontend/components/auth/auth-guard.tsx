'use client';

import { useUser } from '@clerk/nextjs';
import { useUserSync } from '@/hooks/use-user-sync';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { Loader2, RefreshCw, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

export function AuthGuard({ 
  children, 
  requireAuth = true, 
  redirectTo = '/login' 
}: AuthGuardProps) {
  const { isSignedIn, isLoaded } = useUser();
  const { isSyncing, isSynced, error, redirectPath, refreshUser, retrySync, retryCount, maxRetries } = useUserSync();
  const router = useRouter();
  const [redirectTimeout, setRedirectTimeout] = useState<NodeJS.Timeout | null>(null);
  const lastRedirectRef = useRef<string | null>(null);
  const redirectTimestampRef = useRef<number>(0);
  const REDIRECT_DEBOUNCE = 1000; // Increased to 1 second debounce for redirects
  const MIN_REDIRECT_INTERVAL = 2000; // Minimum 2 seconds between redirects

  useEffect(() => {
    if (isLoaded && !isSignedIn && requireAuth) {
      router.push(redirectTo);
    }
  }, [isLoaded, isSignedIn, requireAuth, redirectTo, router]);

  // Handle redirects based on user status with debouncing
  useEffect(() => {
    if (isLoaded && isSignedIn && isSynced && redirectPath) {
      const currentPath = window.location.pathname;
      
      // Clear any existing timeout
      if (redirectTimeout) {
        clearTimeout(redirectTimeout);
        setRedirectTimeout(null);
      }
      
      // Check if we actually need to redirect
      const needsRedirect = (
        (redirectPath === 'dashboard' && !currentPath.startsWith('/dashboard') && !currentPath.startsWith('/welcome')) ||
        (redirectPath === 'onboarding' && !currentPath.startsWith('/onboarding') && !currentPath.startsWith('/welcome'))
      );
      
      // Prevent duplicate redirects and redirect loops
      const redirectKey = `${redirectPath}-${currentPath}`;
      const now = Date.now();
      const timeSinceLastRedirect = now - redirectTimestampRef.current;
      
      const isLoopingRedirect = (
        (redirectPath === 'dashboard' && currentPath === '/onboarding') ||
        (redirectPath === 'onboarding' && currentPath === '/dashboard')
      );
      
      const isRecentRedirect = timeSinceLastRedirect < MIN_REDIRECT_INTERVAL;
      
      if (needsRedirect && lastRedirectRef.current !== redirectKey && !isLoopingRedirect && !isRecentRedirect) {
        console.log(`🔄 AuthGuard: Planning redirect to ${redirectPath} from ${currentPath}`);
        
        // Debounce the redirect to prevent rapid jumping
        const timeout = setTimeout(() => {
          console.log(`🔄 AuthGuard: Executing redirect to /${redirectPath}`);
          lastRedirectRef.current = redirectKey;
          redirectTimestampRef.current = Date.now();
          router.push(`/${redirectPath}`);
        }, REDIRECT_DEBOUNCE);
        
        setRedirectTimeout(timeout);
      } else if (isLoopingRedirect) {
        console.warn(`⚠️ AuthGuard: Prevented potential redirect loop from ${currentPath} to /${redirectPath}`);
      } else if (isRecentRedirect) {
        console.warn(`⚠️ AuthGuard: Skipping redirect - too soon since last redirect (${timeSinceLastRedirect}ms ago)`);
      } else if (!needsRedirect) {
        console.log(`✅ AuthGuard: No redirect needed. Current path: ${currentPath}, Target: ${redirectPath}`);
      }
    }
    
    // Cleanup timeout on unmount
    return () => {
      if (redirectTimeout) {
        clearTimeout(redirectTimeout);
      }
    };
  }, [isLoaded, isSignedIn, isSynced, redirectPath, router, REDIRECT_DEBOUNCE]);

  // Show loading state while Clerk is loading or user is syncing
  if (!isLoaded || (isSignedIn && !isSynced && isSyncing)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-lg text-muted-foreground">
            {!isLoaded ? 'Loading...' : 'Setting up your account...'}
          </p>
        </div>
      </div>
    );
  }

  // Show error state if user sync failed
  if (isSignedIn && !isSynced && error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 mb-4">
            <AlertCircle className="h-12 w-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Setup Error</h2>
          <p className="text-muted-foreground mb-4">
            {error}
          </p>
          <div className="flex flex-col gap-3">
            <Button
              onClick={refreshUser}
              className="w-full"
              disabled={isSyncing}
            >
              {isSyncing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Refreshing...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Status
                </>
              )}
            </Button>
            {retryCount < maxRetries && (
              <Button
                onClick={retrySync}
                variant="outline"
                className="w-full"
                disabled={isSyncing}
              >
                Retry ({retryCount}/{maxRetries})
              </Button>
            )}
            <Button
              onClick={() => window.location.reload()}
              variant="ghost"
              className="w-full"
            >
              Reload Page
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // If auth is not required or user is properly authenticated, render children
  if (!requireAuth || (isSignedIn && isSynced)) {
    return <>{children}</>;
  }

  // If auth is required but user is not signed in, show loading (will redirect)
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
        <p className="text-lg text-muted-foreground">Redirecting...</p>
      </div>
    </div>
  );
}
