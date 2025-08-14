// Clerk Configuration
// Make sure to set these environment variables in your .env.local file

export const clerkConfig = {
  publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!,
  secretKey: process.env.CLERK_SECRET_KEY!,
  signInUrl: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL || '/login',
  signUpUrl: process.env.NEXT_PUBLIC_CLERK_SIGN_UP_URL || '/signup',
  signInFallbackRedirectUrl: process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL || '/dashboard',
  signUpFallbackRedirectUrl: process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL || '/onboarding',
};

// Environment variables you need to set in .env.local:
// NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
// CLERK_SECRET_KEY=sk_test_your_secret_key_here
// NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
// NEXT_PUBLIC_CLERK_SIGN_UP_URL=/signup
// NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
// NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
