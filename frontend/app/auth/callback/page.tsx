/**
 * Clerk Authentication Callback Page
 * Handles redirects after successful authentication
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { useUserContext } from '@/components/providers/user-provider';

export default function AuthCallbackPage() {
  const { user, isSignedIn } = useUser();
  const { isSynced, isLoading, isError } = useUserContext();
  const router = useRouter();

  useEffect(() => {
    if (isSignedIn && user && isSynced && !isLoading && !isError) {
      // User is authenticated and synced, redirect to dashboard
      router.push('/dashboard');
    } else if (isError) {
      // If there's an error syncing, still redirect but show error
      console.error('User sync error, but proceeding to dashboard');
      router.push('/dashboard');
    }
  }, [isSignedIn, user, isSynced, isLoading, isError, router]);

  if (!isSignedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Authentication failed. Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
        {isLoading && <p className="text-gray-600">Setting up your account...</p>}
        {isSynced && <p className="text-green-600">Account setup complete! Redirecting...</p>}
        {isError && <p className="text-yellow-600">Warning: Some account setup failed, but continuing...</p>}
      </div>
    </div>
  );
}
