import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Generate a random string for OAuth state and PKCE
 */
export function generateRandomString(length: number): string {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return result;
}

/**
 * Generate a secure random string using crypto API if available
 */
export function generateSecureRandomString(length: number): string {
  if (typeof window !== 'undefined' && window.crypto) {
    const array = new Uint8Array(length);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('').substring(0, length);
  }
  return generateRandomString(length);
}

/**
 * Encode string to base64 URL safe
 */
export function base64UrlEncode(str: string): string {
  return btoa(str)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Decode base64 URL safe string
 */
export function base64UrlDecode(str: string): string {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return atob(str);
}

/**
 * Generate SHA256 hash for PKCE
 */
export async function generateCodeChallenge(codeVerifier: string): Promise<string> {
  if (typeof window !== 'undefined' && window.crypto) {
    const encoder = new TextEncoder();
    const data = encoder.encode(codeVerifier);
    const hash = await window.crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hash));
    return base64UrlEncode(String.fromCharCode(...hashArray));
  }
  // Fallback for environments without crypto API
  return codeVerifier;
}

/**
 * Format platform name for display
 */
export function formatPlatformName(platform: string): string {
  const platformNames: Record<string, string> = {
    instagram: 'Instagram',
    facebook: 'Facebook',
    twitter: 'Twitter/X',
    linkedin: 'LinkedIn',
    youtube: 'YouTube',
  };
  return platformNames[platform] || platform;
}

/**
 * Get platform icon
 */
export function getPlatformIcon(platform: string): string {
  const platformIcons: Record<string, string> = {
    instagram: '📷',
    facebook: '📘',
    twitter: '🐦',
    linkedin: '💼',
    youtube: '📺',
  };
  return platformIcons[platform] || '🔗';
}

/**
 * Get platform color class
 */
export function getPlatformColor(platform: string): string {
  const platformColors: Record<string, string> = {
    instagram: 'bg-pink-600',
    facebook: 'bg-blue-600',
    twitter: 'bg-black',
    linkedin: 'bg-blue-700',
    youtube: 'bg-red-600',
  };
  return platformColors[platform] || 'bg-gray-600';
}
