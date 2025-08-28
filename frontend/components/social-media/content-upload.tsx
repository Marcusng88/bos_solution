'use client';

import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/nextjs';
import { useSocialAccounts } from '@/lib/use-social-accounts';

interface MediaFile {
  url: string;
  type: string;
  size?: number;
  filename?: string;
  mimeType?: string;
}

export default function ContentUpload() {
  const { user } = useUser();
  const { 
    accounts, 
    isLoading, 
    lastSyncTime, 
    refreshAccounts, 
    getAccountByPlatform 
  } = useSocialAccounts();
  
  const [templates, setTemplates] = useState<any[]>([]);
  const [message, setMessage] = useState('');

  // Form state
  const [title, setTitle] = useState('');
  const [contentText, setContentText] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [selectedAccount, setSelectedAccount] = useState('');
  const [isTestPost, setIsTestPost] = useState(false); // Default to real posts
  const [scheduledAt, setScheduledAt] = useState('');
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);

  // Load templates when component mounts
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = () => {
    // TODO: Implement templates later
    setTemplates([]);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newMediaFiles: MediaFile[] = Array.from(files).map(file => ({
        url: URL.createObjectURL(file),
        type: file.type.startsWith('image/') ? 'image' : 'video',
        size: file.size,
        filename: file.name,
        mimeType: file.type
      }));
      setMediaFiles(prev => [...prev, ...newMediaFiles]);
    }
  };

  const removeMediaFile = (index: number) => {
    setMediaFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !selectedAccount) return;

    setMessage('');

    try {
      // TODO: Implement actual content upload to backend
      setMessage(`Content ready for ${isTestPost ? 'test posting' : 'real posting'}! (Backend integration pending)`);
      
      // Reset form
      setTitle('');
      setContentText('');
      setSelectedPlatform('');
      setSelectedAccount('');
      setScheduledAt('');
      setMediaFiles([]);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessage('Failed to upload content');
    }
  };

  // TODO: Implement post now functionality when backend is ready

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'instagram': return '📸';
      case 'facebook': return '📘';
      case 'twitter': return '🐦';
      case 'linkedin': return '💼';
      // tiktok removed
      case 'youtube': return '📺';
      default: return '🌐';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Social Media Content Upload</h1>
        <p className="text-gray-600">
          Create and schedule content for your social media accounts. 
          <span className="text-red-600 font-semibold"> Posts will be published to your real accounts!</span>
        </p>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.includes('successfully') 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message}
        </div>
      )}

      {/* Account Connection Status */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-blue-900">Connected Accounts</h3>
          <button
            onClick={refreshAccounts}
            disabled={isLoading}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {isLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        
        {isLoading ? (
          <div className="text-blue-700">Loading your accounts...</div>
        ) : accounts.length === 0 ? (
          <div className="space-y-3">
            <p className="text-blue-700">
              No social media accounts connected yet. 
            </p>
            <div className="text-sm text-blue-600">
              <p className="font-medium">To connect your accounts:</p>
              <ol className="list-decimal list-inside mt-1 space-y-1">
                <li>Add your Facebook access token to the backend .env file</li>
                <li>Make sure your Instagram business account is linked to Facebook</li>
                <li>Click refresh to load your accounts</li>
              </ol>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {accounts.map(account => (
              <div key={account.accountId} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-blue-200">
                {account.profilePicture ? (
                  <img 
                    src={account.profilePicture} 
                    alt={account.username}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {account.username.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{account.accountName}</div>
                  <div className="text-sm text-blue-600">@{account.username}</div>
                </div>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓ Connected
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Content Upload Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Platform and Account Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select Platform</option>
              <option value="instagram">📸 Instagram</option>
              <option value="facebook">📘 Facebook</option>
              <option value="twitter">🐦 Twitter</option>
              <option value="linkedin">💼 LinkedIn</option>
              {/* TikTok removed */}
              <option value="youtube">📺 YouTube</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account
            </label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select Account</option>
              {accounts
                .filter(acc => !selectedPlatform || acc.platform === selectedPlatform)
                .map(account => (
                  <option key={account.accountId} value={account.accountId}>
                    {account.accountName}
                  </option>
                ))}
            </select>
          </div>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title (Optional)
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter post title..."
          />
        </div>

        {/* Content Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content Text *
          </label>
          <textarea
            value={contentText}
            onChange={(e) => setContentText(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Write your post content here..."
            required
          />
          <div className="mt-2 text-sm text-gray-500">
            Character count: {contentText.length}
            {selectedPlatform === 'twitter' && contentText.length > 280 && (
              <span className="text-red-500 ml-2">⚠️ Exceeds Twitter limit (280)</span>
            )}
            {selectedPlatform === 'instagram' && contentText.length > 2200 && (
              <span className="text-red-500 ml-2">⚠️ Exceeds Instagram limit (2200)</span>
            )}
          </div>
        </div>

        {/* Media Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Media Files
          </label>
          <input
            type="file"
            multiple
            accept="image/*,video/*"
            onChange={handleFileUpload}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {mediaFiles.length > 0 && (
            <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3">
              {mediaFiles.map((file, index) => (
                <div key={index} className="relative">
                  {file.type === 'image' ? (
                    <img
                      src={file.url}
                      alt={file.filename || `Media ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                  ) : (
                    <div className="w-full h-24 bg-gray-100 rounded-lg flex items-center justify-center">
                      <span className="text-gray-500">🎥 Video</span>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => removeMediaFile(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Scheduling */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Schedule (Optional)
          </label>
          <input
            type="datetime-local"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Leave empty to save as draft
          </p>
        </div>

        {/* Test Mode Toggle */}
        <div className="flex items-center space-x-3 p-4 bg-red-50 rounded-lg border border-red-200">
          <input
            type="checkbox"
            id="testMode"
            checked={isTestPost}
            onChange={(e) => setIsTestPost(e.target.checked)}
            className="w-4 h-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
          />
          <label htmlFor="testMode" className="text-sm font-medium text-red-800">
            Test Mode (Optional)
          </label>
          <span className="text-xs text-red-700">
            When enabled, content won't be posted to real social media accounts
          </span>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!selectedAccount || !contentText}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isTestPost ? 'Save as Test Post' : 'Publish Now'}
        </button>
      </form>

      {/* Post Preview Section */}
      {contentText && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Post Preview</h3>
          
          {/* Platform Selection for Preview */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Preview on Platform:</label>
            <div className="flex flex-wrap gap-2">
              {['facebook', 'instagram'].map(platform => {
                const account = accounts.find(acc => acc.platform === platform);
                return (
                  <label key={platform} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedPlatform === platform}
                      onChange={() => setSelectedPlatform(platform)}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm font-medium capitalize">{platform}</span>
                    {account ? (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                        ✓ {account.username}
                      </span>
                    ) : (
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                        Not connected
                      </span>
                    )}
                  </label>
                );
              })}
            </div>
          </div>

          {/* Preview Content */}
          {selectedPlatform && (
            <div className="space-y-4">
              {/* Facebook Preview */}
              {selectedPlatform === 'facebook' && (
                <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    {(() => {
                      const account = accounts.find(acc => acc.platform === 'facebook');
                      return account?.profilePicture ? (
                        <img 
                          src={account.profilePicture} 
                          alt={account.username}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {account?.username?.charAt(0)?.toUpperCase() || 'F'}
                        </div>
                      );
                    })()}
                    <div>
                      <div className="font-semibold text-gray-900">
                        {accounts.find(acc => acc.platform === 'facebook')?.accountName || 'Your Business'}
                      </div>
                      <div className="text-sm text-gray-500">2 hours ago</div>
                    </div>
                  </div>
                  <div className="text-gray-900 mb-3">{contentText}</div>
                  {mediaFiles.length > 0 && (
                    <div className="mb-3">
                      <img 
                        src={mediaFiles[0].url} 
                        alt="Preview" 
                        className="w-full h-48 object-cover rounded-lg"
                      />
                    </div>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>❤️ 42</span>
                    <span>💬 8 comments</span>
                    <span>🔄 3 shares</span>
                  </div>
                </div>
              )}

              {/* Instagram Preview */}
              {selectedPlatform === 'instagram' && (
                <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm max-w-sm">
                  <div className="flex items-center gap-3 mb-3">
                    {(() => {
                      const account = accounts.find(acc => acc.platform === 'instagram');
                      return account?.profilePicture ? (
                        <img 
                          src={account.profilePicture} 
                          alt={account.username}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {account?.username?.charAt(0)?.toUpperCase() || 'I'}
                        </div>
                      );
                    })()}
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900">
                        {accounts.find(acc => acc.platform === 'instagram')?.username || 'your_business'}
                      </div>
                      <div className="text-xs text-gray-500">Sponsored</div>
                    </div>
                  </div>
                  {mediaFiles.length > 0 && (
                    <div className="mb-3">
                      <img 
                        src={mediaFiles[0].url} 
                        alt="Preview" 
                        className="w-full h-64 object-cover rounded-lg"
                      />
                    </div>
                  )}
                  <div className="flex items-center gap-4 mb-2">
                    <span>❤️</span>
                    <span>💬</span>
                    <span>📤</span>
                  </div>
                  <div className="text-sm text-gray-900 mb-1">
                    <span className="font-semibold">{accounts.find(acc => acc.platform === 'instagram')?.username || 'your_business'}</span> {contentText}
                  </div>
                  <div className="text-xs text-gray-500">1,234 likes</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Recent Uploads */}
      <div className="mt-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Uploads</h3>
        {/* TODO: Implement recent uploads display */}
        <p className="text-gray-500 text-center py-8">
          Recent uploads will appear here
        </p>
      </div>
    </div>
  );
}
