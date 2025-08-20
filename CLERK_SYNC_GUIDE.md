# Clerk to Supabase User Sync Integration Guide

This document explains how the Clerk authentication is integrated with the Supabase backend to automatically sync user data after sign-in.

## Flow Overview

1. User signs in with Clerk (frontend)
2. Clerk redirects to callback page
3. Frontend automatically syncs user data to backend
4. Backend stores/updates user data in Supabase
5. User monitoring settings are automatically created (via database trigger)
6. User is redirected to dashboard

## Backend Implementation

### 1. User Model (`app/models/user.py`)
- Matches the Supabase `users` table structure exactly
- Uses UUID primary key and clerk_id as unique identifier
- Includes all fields: email, first_name, last_name, profile_image_url, is_active

### 2. User Schemas (`app/schemas/user.py`)
- `ClerkUserData`: Schema for receiving Clerk user data
- `UserCreate`: Schema for creating new users
- `UserResponse`: Schema for API responses
- Helper method to extract primary email from Clerk's email array

### 3. API Endpoints (`app/api/v1/endpoints/users.py`)
- `POST /api/v1/users/sync`: Sync user from Clerk data
- `GET /api/v1/users/profile`: Get user profile
- Existing user settings endpoints

### 4. Database Triggers
- Automatic user_monitoring_settings creation when user is created
- Updated_at timestamp updates on user changes

## Frontend Implementation

### 1. API Client (`lib/api-client.ts`)
- Added `syncUserFromClerk()` method
- Handles authentication headers

### 2. User Sync Hook (`hooks/use-user-sync.ts`)
- Custom hook that automatically syncs user data after Clerk sign-in
- Transforms Clerk user data to match backend schema
- Handles loading states and error handling

### 3. User Provider (`components/providers/user-provider.tsx`)
- React context for managing user sync state
- Visual feedback component for sync status

### 4. Auth Callback (`app/auth/callback/page.tsx`)
- Handles post-authentication redirects
- Waits for user sync to complete before redirecting to dashboard

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key
CLERK_SECRET_KEY=sk_test_your_secret
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/auth/callback
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/auth/callback
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Usage

### Automatic Sync
The sync happens automatically when:
1. User signs in with Clerk
2. `useUserSync` hook detects signed-in user
3. Calls `/users/sync` endpoint with Clerk user data

### Manual Sync
```typescript
const { syncUser } = useUserSync();
await syncUser();
```

### Getting User Data
```typescript
// Get synced user profile
const profile = await apiClient.getUserProfile(userId);

// Get user settings (auto-created)
const settings = await apiClient.getUserSettings(userId);
```

## Error Handling

The system handles various error scenarios:
- Network failures during sync
- Database connection issues
- Invalid user data
- Missing required fields

Visual feedback is provided to users during the sync process.

## Testing

1. Sign up/in with Clerk
2. Check that user appears in Supabase `users` table
3. Verify `user_monitoring_settings` was created automatically
4. Confirm user is redirected to dashboard after successful sync

## Database Schema Consistency

The user model strictly follows the Supabase table structure:
```sql
CREATE TABLE public.users (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    clerk_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NULL,
    profile_image_url VARCHAR(500) NULL,
    is_active BOOLEAN NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NOW(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_clerk_id_key UNIQUE (clerk_id)
);
```

This ensures compatibility with existing Supabase tables and triggers.
