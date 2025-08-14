# Clerk Authentication Setup Guide

This guide will help you set up Clerk authentication for your BOS Solution frontend.

## Prerequisites

- A Clerk account (sign up at [clerk.com](https://clerk.com))
- Your BOS Solution frontend project

## Step 1: Create a Clerk Application

1. Go to [Clerk Dashboard](https://dashboard.clerk.com/)
2. Click "Add Application"
3. Choose "Next.js" as your framework
4. Give your application a name (e.g., "BOS Solution")
5. Click "Create Application"

## Step 2: Configure Clerk Application

### General Settings
1. In your Clerk dashboard, go to **API Keys**
2. Copy your **Publishable Key** and **Secret Key**
3. Go to **User & Authentication** → **Email, Phone, Username**
4. Enable the authentication methods you want (Email, Username, etc.)

### Redirect URLs
1. Go to **Paths** in your Clerk dashboard
2. Set the following paths:
   - **Sign in URL**: `/login`
   - **Sign up URL**: `/signup`
   - **After sign in URL**: `/dashboard`
   - **After sign up URL**: `/onboarding`

### CORS Settings
1. Go to **Paths** → **CORS**
2. Add your frontend domain:
   - For development: `http://localhost:3000`
   - For production: `https://yourdomain.com`

## Step 3: Install Clerk Package

```bash
cd frontend
npm install @clerk/nextjs
```

## Step 4: Environment Configuration

Create a `.env.local` file in your frontend directory:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/login
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/signup
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

**Important**: Replace the placeholder values with your actual Clerk keys.

## Step 5: Update Your Application

The Clerk integration has already been set up in your project:

### 1. Clerk Provider
- Located at: `components/providers/clerk-provider.tsx`
- Wraps your app to provide authentication context
- Uses the new prop names: `signInFallbackRedirectUrl` and `signUpFallbackRedirectUrl`

### 2. Middleware
- Located at: `middleware.ts`
- Protects routes and handles authentication

### 3. Layout Integration
- Updated `app/layout.tsx` to include ClerkProviderWrapper

## Step 6: Test the Setup

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Navigate to `http://localhost:3000`
3. You should be redirected to `/login` if not authenticated
4. Try signing up with a new account
5. After signup, you should be redirected to `/onboarding`
6. After signin, you should be redirected to `/dashboard`

## Step 7: Customize Authentication UI

### Using Pre-built Components

Clerk provides pre-built components that you can use directly:

```tsx
import { SignIn, SignUp, UserButton } from '@clerk/nextjs';

// In your login page
export default function LoginPage() {
  return <SignIn fallbackRedirectUrl="/dashboard" />;
}

// In your signup page
export default function SignupPage() {
  return <SignUp fallbackRedirectUrl="/onboarding" />;
}

// In your dashboard
export default function Dashboard() {
  return (
    <div>
      <UserButton signOutFallbackRedirectUrl="/" />
      <h1>Dashboard</h1>
    </div>
  );
}
```

### Using Hooks

```tsx
import { useUser, useAuth } from '@clerk/nextjs';

export default function MyComponent() {
  const { user, isLoaded } = useUser();
  const { signOut } = useAuth();

  if (!isLoaded) return <div>Loading...</div>;
  
  if (!user) return <div>Please sign in</div>;

  return (
    <div>
      <p>Hello, {user.firstName}!</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}
```

## Step 8: Backend Integration

Your backend is already configured to work with Clerk:

1. The backend expects Clerk JWT tokens in the Authorization header
2. Use the `verify_clerk_token` dependency in your API endpoints
3. The backend will verify tokens with Clerk's API

### Example API Call

```typescript
// In your frontend components
import { useAuth } from '@clerk/nextjs';

export function MyComponent() {
  const { getToken } = useAuth();
  
  const callApi = async () => {
    const token = await getToken();
    
    const response = await fetch('/api/v1/protected-endpoint', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    // Handle response
  };
  
  return <button onClick={callApi}>Call API</button>;
}
```

## Important Notes

- **New Prop Names**: The project now uses the latest Clerk prop names:
  - `fallbackRedirectUrl` instead of `redirectUrl`
  - `signInFallbackRedirectUrl` instead of `afterSignInUrl`
  - `signUpFallbackRedirectUrl` instead of `afterSignUpUrl`
  - `signOutFallbackRedirectUrl` instead of `afterSignOutUrl`

- **Development vs Production**: Make sure to update your environment variables when deploying to production
- **CORS**: Ensure your Clerk dashboard has the correct CORS settings for your production domain

## Troubleshooting

### Common Issues

1. **Redirect not working**: Check that your Clerk dashboard has the correct redirect URLs configured
2. **CORS errors**: Verify your domain is added to the CORS settings in Clerk
3. **Environment variables**: Ensure all required environment variables are set in your `.env.local` file

### Getting Help

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Community](https://community.clerk.com/)
- [Clerk Support](https://clerk.com/support)

## Files Modified

The following files have been created/modified for Clerk integration:

- ✅ `components/providers/clerk-provider.tsx` - Clerk provider wrapper
- ✅ `middleware.ts` - Authentication middleware
- ✅ `app/layout.tsx` - Updated to include Clerk provider
- ✅ `lib/clerk.ts` - Clerk configuration
- ✅ `CLERK_SETUP.md` - This setup guide

Your Clerk integration is now ready to use! 🎉
