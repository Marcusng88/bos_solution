/**
 * User Provider Component
 * Handles automatic user sync with backend after Clerk authentication
 */

'use client';

import React, { createContext, useContext } from 'react';
import { useUserSync, UserProfile, UserSettings } from '../../hooks/use-user-sync';

interface UserContextType {
  isLoading: boolean;
  isError: boolean;
  error?: string;
  isSynced: boolean;
  syncUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | null>(null);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const syncData = useUserSync();

  return (
    <UserContext.Provider value={syncData}>
      {children}
    </UserContext.Provider>
  );
}

export function useUserContext() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUserContext must be used within a UserProvider');
  }
  return context;
}

// Loading component for user sync
export function UserSyncStatus() {
  const { isLoading, isError, error, isSynced } = useUserContext();

  if (!isLoading && !isError && isSynced) {
    return null; // Don't show anything when sync is complete
  }

  if (isLoading) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-blue-500 text-white p-2 text-center text-sm z-50">
        Syncing user data...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-red-500 text-white p-2 text-center text-sm z-50">
        Error syncing user data: {error}
      </div>
    );
  }

  return null;
}
