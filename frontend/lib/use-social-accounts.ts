/**
 * Hook for managing social media accounts
 * Provides functionality for connecting, syncing, and managing social media accounts
 */

import { useState, useEffect, useCallback } from 'react'

export interface SocialAccount {
  id: string
  platform: string
  username: string
  displayName: string
  profilePicture?: string
  isConnected: boolean
  lastSyncTime?: string
  followerCount?: number
  accountType: 'personal' | 'business' | 'creator'
  permissions: string[]
}

export interface UseSocialAccountsOptions {
  autoSync?: boolean
  syncInterval?: number
}

export function useSocialAccounts(options: UseSocialAccountsOptions = {}) {
  const { autoSync = true, syncInterval = 300000 } = options // 5 minutes default

  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [lastSyncTime, setLastSyncTime] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Mock data for development
  const mockAccounts: SocialAccount[] = [
    {
      id: '1',
      platform: 'instagram',
      username: 'techcompany',
      displayName: 'Tech Company',
      profilePicture: 'https://via.placeholder.com/150',
      isConnected: true,
      lastSyncTime: new Date().toISOString(),
      followerCount: 15420,
      accountType: 'business',
      permissions: ['read', 'write', 'publish']
    },
    {
      id: '2',
      platform: 'linkedin',
      username: 'techcompany',
      displayName: 'Tech Company',
      profilePicture: 'https://via.placeholder.com/150',
      isConnected: true,
      lastSyncTime: new Date().toISOString(),
      followerCount: 8920,
      accountType: 'business',
      permissions: ['read', 'write', 'publish']
    },
    {
      id: '3',
      platform: 'twitter',
      username: 'techcompany',
      displayName: 'Tech Company',
      profilePicture: 'https://via.placeholder.com/150',
      isConnected: true,
      lastSyncTime: new Date().toISOString(),
      followerCount: 12340,
      accountType: 'business',
      permissions: ['read', 'write', 'publish']
    },
    {
      id: '4',
      platform: 'facebook',
      username: 'techcompany',
      displayName: 'Tech Company',
      profilePicture: 'https://via.placeholder.com/150',
      isConnected: false,
      lastSyncTime: undefined,
      followerCount: undefined,
      accountType: 'business',
      permissions: []
    },
    {
      id: '5',
      platform: 'youtube',
      username: 'techcompany',
      displayName: 'Tech Company',
      profilePicture: 'https://via.placeholder.com/150',
      isConnected: false,
      lastSyncTime: undefined,
      followerCount: undefined,
      accountType: 'business',
      permissions: []
    }
  ]

  // Load accounts
  const loadAccounts = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // In a real implementation, this would call an API
      // For now, we'll use mock data
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API delay
      
      setAccounts(mockAccounts)
      setLastSyncTime(new Date().toISOString())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load accounts')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Refresh accounts
  const refreshAccounts = useCallback(async () => {
    await loadAccounts()
  }, [loadAccounts])

  // Connect account
  const connectAccount = useCallback(async (platform: string) => {
    try {
      setIsLoading(true)
      setError(null)
      
      // In a real implementation, this would initiate OAuth flow
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate OAuth delay
      
      // For demo purposes, we'll just mark the account as connected
      setAccounts(prev => prev.map(account => 
        account.platform === platform 
          ? { ...account, isConnected: true, lastSyncTime: new Date().toISOString() }
          : account
      ))
      
      return { success: true }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect account')
      return { success: false, error: err instanceof Error ? err.message : 'Failed to connect account' }
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Disconnect account
  const disconnectAccount = useCallback(async (platform: string) => {
    try {
      setIsLoading(true)
      setError(null)
      
      // In a real implementation, this would revoke OAuth tokens
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API delay
      
      setAccounts(prev => prev.map(account => 
        account.platform === platform 
          ? { ...account, isConnected: false, lastSyncTime: undefined }
          : account
      ))
      
      return { success: true }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect account')
      return { success: false, error: err instanceof Error ? err.message : 'Failed to disconnect account' }
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Get account by platform
  const getAccountByPlatform = useCallback((platform: string) => {
    return accounts.find(account => account.platform === platform)
  }, [accounts])

  // Get connected accounts
  const getConnectedAccounts = useCallback(() => {
    return accounts.filter(account => account.isConnected)
  }, [accounts])

  // Get disconnected accounts
  const getDisconnectedAccounts = useCallback(() => {
    return accounts.filter(account => !account.isConnected)
  }, [accounts])

  // Check if platform is supported
  const isPlatformSupported = useCallback((platform: string) => {
    const supportedPlatforms = ['instagram', 'linkedin', 'twitter', 'facebook', 'youtube', 'tiktok']
    return supportedPlatforms.includes(platform)
  }, [])

  // Auto-sync accounts
  useEffect(() => {
    if (autoSync) {
      loadAccounts()
      
      const interval = setInterval(() => {
        refreshAccounts()
      }, syncInterval)
      
      return () => clearInterval(interval)
    }
  }, [autoSync, syncInterval, loadAccounts, refreshAccounts])

  return {
    // State
    accounts,
    isLoading,
    lastSyncTime,
    error,
    
    // Actions
    loadAccounts,
    refreshAccounts,
    connectAccount,
    disconnectAccount,
    
    // Utilities
    getAccountByPlatform,
    getConnectedAccounts,
    getDisconnectedAccounts,
    isPlatformSupported,
    
    // Computed values
    connectedCount: accounts.filter(a => a.isConnected).length,
    totalCount: accounts.length,
    hasConnectedAccounts: accounts.some(a => a.isConnected),
    hasError: !!error
  }
}
