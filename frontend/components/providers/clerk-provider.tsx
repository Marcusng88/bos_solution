"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { ReactNode } from "react";
import { clerkConfig } from "@/lib/clerk";
import { UserProvider, UserSyncStatus } from "./user-provider";

interface ClerkProviderWrapperProps {
  children: ReactNode;
}

export function ClerkProviderWrapper({ children }: ClerkProviderWrapperProps) {
  return (
    <ClerkProvider
      publishableKey={clerkConfig.publishableKey}
      signInUrl={clerkConfig.signInUrl}
      signUpUrl={clerkConfig.signUpUrl}
      signInFallbackRedirectUrl={clerkConfig.signInFallbackRedirectUrl}
      signUpFallbackRedirectUrl={clerkConfig.signUpFallbackRedirectUrl}
    >
      <UserProvider>
        <UserSyncStatus />
        {children}
      </UserProvider>
    </ClerkProvider>
  );
}
