'use client';

import { useUser } from '@clerk/nextjs';
import { useUserSync } from '@/hooks/use-user-sync';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';

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
  const { isSyncing, isSynced, error } = useUserSync();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !isSignedIn && requireAuth) {
      router.push(redirectTo);
    }
  }, [isLoaded, isSignedIn, requireAuth, redirectTo, router]);

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
            <svg className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold mb-2">Setup Error</h2>
          <p className="text-muted-foreground mb-4">
            There was an error setting up your account. Please try refreshing the page.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Refresh Page
          </button>
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
