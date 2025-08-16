/**
 * OAuth Utilities for Meta Platforms (Instagram, Facebook)
 * Handles OAuth flows, state management, and token exchange
 */

import { generateRandomString } from './utils';

// OAuth configuration
const OAUTH_CONFIG = {
  redirectBaseUrl: process.env.NEXT_PUBLIC_OAUTH_REDIRECT_BASE_URL || 'http://localhost:3000/auth/callback',
  successUrl: process.env.NEXT_PUBLIC_OAUTH_SUCCESS_URL || 'http://localhost:3000/dashboard',
  errorUrl: process.env.NEXT_PUBLIC_OAUTH_ERROR_URL || 'http://localhost:3000/auth/error',
};

// Platform-specific OAuth configurations
export const PLATFORM_CONFIG = {
  instagram: {
    name: 'Instagram',
    authUrl: 'https://api.instagram.com/oauth/authorize',
    tokenUrl: 'https://api.instagram.com/oauth/access_token',
    scopes: ['instagram_basic', 'instagram_content_publish'],
    clientId: process.env.NEXT_PUBLIC_INSTAGRAM_APP_ID,
    icon: '📷',
    color: 'bg-pink-600',
  },
  facebook: {
    name: 'FB/Ins',
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token',
    scopes: [
      'pages_read_engagement', 
      'pages_show_list', 
      'pages_manage_metadata',
      'pages_read_user_content',  // For Instagram access
      'instagram_basic',          // Instagram basic access
      'instagram_content_publish' // Instagram posting access
    ],
    clientId: process.env.NEXT_PUBLIC_FACEBOOK_APP_ID,
    icon: '📘',
    color: 'bg-blue-600',
  },
  twitter: {
    name: 'Twitter/X',
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    scopes: ['tweet.read', 'users.read', 'offline.access'],
    clientId: process.env.NEXT_PUBLIC_TWITTER_APP_ID,
    icon: '🐦',
    color: 'bg-black',
  },
  linkedin: {
    name: 'LinkedIn',
    authUrl: 'https://www.linkedin.com/oauth/v2/authorization',
    tokenUrl: 'https://www.linkedin.com/oauth/v2/accessToken',
    scopes: ['r_liteprofile', 'r_emailaddress', 'w_member_social'],
    clientId: process.env.NEXT_PUBLIC_LINKEDIN_APP_ID,
    icon: '💼',
    color: 'bg-blue-700',
  },
  youtube: {
    name: 'YouTube',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: ['https://www.googleapis.com/auth/youtube.readonly'],
    clientId: process.env.NEXT_PUBLIC_YOUTUBE_APP_ID,
    icon: '📺',
    color: 'bg-red-600',
  },
};

// OAuth state management
export interface OAuthState {
  platform: string;
  state: string;
  codeVerifier?: string;
  redirectUri: string;
  requestedScopes: string[];
  timestamp: number;
}

/**
 * Generate OAuth state for security
 */
export function generateOAuthState(platform: string, requestedScopes: string[]): OAuthState {
  return {
    platform,
    state: generateRandomString(32),
    codeVerifier: generateRandomString(128), // For PKCE
    redirectUri: `${OAUTH_CONFIG.redirectBaseUrl}/${platform}`,
    requestedScopes,
    timestamp: Date.now(),
  };
}

/**
 * Store OAuth state in session storage
 */
export function storeOAuthState(state: OAuthState): void {
  try {
    sessionStorage.setItem(`oauth_state_${state.platform}`, JSON.stringify(state));
  } catch (error) {
    console.error('Failed to store OAuth state:', error);
  }
}

/**
 * Retrieve OAuth state from session storage
 */
export function getOAuthState(platform: string): OAuthState | null {
  try {
    const stored = sessionStorage.getItem(`oauth_state_${platform}`);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to retrieve OAuth state:', error);
    return null;
  }
}

/**
 * Clear OAuth state from session storage
 */
export function clearOAuthState(platform: string): void {
  try {
    sessionStorage.removeItem(`oauth_state_${platform}`);
  } catch (error) {
    console.error('Failed to clear OAuth state:', error);
  }
}

/**
 * Validate OAuth state (prevent CSRF attacks)
 */
export function validateOAuthState(platform: string, state: string): boolean {
  const storedState = getOAuthState(platform);
  if (!storedState) return false;
  
  // Check if state matches and is not expired (5 minutes)
  const isExpired = Date.now() - storedState.timestamp > 5 * 60 * 1000;
  const isValid = storedState.state === state && !isExpired;
  
  if (isValid) {
    clearOAuthState(platform); // Clean up after successful validation
  }
  
  return isValid;
}

/**
 * Build OAuth authorization URL for Instagram
 */
export function buildInstagramAuthUrl(state: OAuthState): string {
  const config = PLATFORM_CONFIG.instagram;
  const params = new URLSearchParams({
    client_id: config.clientId || '',
    redirect_uri: state.redirectUri,
    scope: state.requestedScopes.join(','),
    response_type: 'code',
    state: state.state,
  });
  
  return `${config.authUrl}?${params.toString()}`;
}

/**
 * Build OAuth authorization URL for Facebook
 */
export function buildFacebookAuthUrl(state: OAuthState): string {
  const config = PLATFORM_CONFIG.facebook;
  const params = new URLSearchParams({
    client_id: config.clientId || '',
    redirect_uri: state.redirectUri,
    scope: state.requestedScopes.join(','),
    response_type: 'code',
    state: state.state,
  });
  
  return `${config.authUrl}?${params.toString()}`;
}

/**
 * Build OAuth authorization URL for any platform
 */
export function buildOAuthUrl(platform: string, state: OAuthState): string {
  switch (platform) {
    case 'instagram':
      return buildInstagramAuthUrl(state);
    case 'facebook':
      return buildFacebookAuthUrl(state);
    case 'twitter':
      return buildTwitterAuthUrl(state);
    case 'linkedin':
      return buildLinkedInAuthUrl(state);
    case 'youtube':
      return buildYouTubeAuthUrl(state);
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}

/**
 * Build OAuth authorization URL for Twitter
 */
export function buildTwitterAuthUrl(state: OAuthState): string {
  const config = PLATFORM_CONFIG.twitter;
  const params = new URLSearchParams({
    client_id: config.clientId || '',
    redirect_uri: state.redirectUri,
    scope: state.requestedScopes.join(' '),
    response_type: 'code',
    state: state.state,
    code_challenge: state.codeVerifier || '',
    code_challenge_method: 'S256',
  });
  
  return `${config.authUrl}?${params.toString()}`;
}

/**
 * Build OAuth authorization URL for LinkedIn
 */
export function buildLinkedInAuthUrl(state: OAuthState): string {
  const config = PLATFORM_CONFIG.linkedin;
  const params = new URLSearchParams({
    client_id: config.clientId || '',
    redirect_uri: state.redirectUri,
    scope: state.requestedScopes.join(' '),
    response_type: 'code',
    state: state.state,
  });
  
  return `${config.authUrl}?${params.toString()}`;
}

/**
 * Build OAuth authorization URL for YouTube
 */
export function buildYouTubeAuthUrl(state: OAuthState): string {
  const config = PLATFORM_CONFIG.youtube;
  const params = new URLSearchParams({
    client_id: config.clientId || '',
    redirect_uri: state.redirectUri,
    scope: state.requestedScopes.join(' '),
    response_type: 'code',
    state: state.state,
    access_type: 'offline',
    prompt: 'consent',
  });
  
  return `${config.authUrl}?${params.toString()}`;
}

/**
 * Initiate OAuth flow for a platform
 */
export function initiateOAuth(platform: string, requestedScopes?: string[]): void {
  const config = PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG];
  if (!config) {
    throw new Error(`Unsupported platform: ${platform}`);
  }
  
  const scopes = requestedScopes || config.scopes;
  const state = generateOAuthState(platform, scopes);
  
  // Store state for validation
  storeOAuthState(state);
  
  // Build and navigate to OAuth URL
  const authUrl = buildOAuthUrl(platform, state);
  window.location.href = authUrl;
}

/**
 * Handle OAuth callback and extract authorization code
 */
export function handleOAuthCallback(platform: string, url: string): { code: string; state: string } | null {
  const urlParams = new URLSearchParams(url.split('?')[1]);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');
  
  if (error) {
    console.error(`OAuth error for ${platform}:`, error);
    return null;
  }
  
  if (!code || !state) {
    console.error(`Missing OAuth parameters for ${platform}`);
    return null;
  }
  
  // Validate state to prevent CSRF
  if (!validateOAuthState(platform, state)) {
    console.error(`Invalid OAuth state for ${platform}`);
    return null;
  }
  
  return { code, state };
}

/**
 * Get platform configuration
 */
export function getPlatformConfig(platform: string) {
  return PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG];
}

/**
 * Get all available platforms
 */
export function getAvailablePlatforms() {
  return Object.keys(PLATFORM_CONFIG).map(platform => ({
    id: platform,
    ...getPlatformConfig(platform),
  }));
}

/**
 * Check if platform is supported
 */
export function isPlatformSupported(platform: string): boolean {
  return platform in PLATFORM_CONFIG;
}
