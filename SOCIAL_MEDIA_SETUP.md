# 🚀 Social Media Integration Setup Guide

## Overview
This guide will help you connect your social media accounts to post content directly from your dashboard.

## 🔑 Required API Keys

### Facebook & Instagram
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use existing one
3. Add Facebook Login and Instagram Basic Display products
4. Get your App ID and App Secret
5. Generate a Page Access Token for your Facebook page
6. For Instagram, connect your Instagram Business account

**Environment Variables:**
```bash
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_page_access_token
```

### Twitter
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Get your API Key, API Secret, and Bearer Token
4. Generate Access Token and Access Token Secret

**Environment Variables:**
```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### LinkedIn
1. Go to [LinkedIn Developers](https://developer.linkedin.com/)
2. Create a new app
3. Get your Client ID and Client Secret
4. Generate an Access Token

**Environment Variables:**
```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
```

## 📝 Setup Steps

### 1. Add Environment Variables
Add the above environment variables to your backend `.env` file.

### 2. Restart Backend
Restart your FastAPI backend to load the new environment variables.

### 3. Connect Accounts
1. Go to Dashboard → Publishing → Social Media
2. Click "Connect Account" for your desired platform
3. Enter your account details and access tokens

### 4. Start Posting!
Once connected, you can:
- Write content with character limits for each platform
- Upload media files
- Schedule posts
- Post immediately to your real accounts

## ⚠️ Important Notes

- **Real Posts**: Content will be posted to your actual social media accounts
- **Test Mode**: Optional toggle to save as draft without posting
- **API Limits**: Respect each platform's rate limits
- **Media Upload**: Currently supports text posts, media uploads coming soon

## 🆘 Troubleshooting

### "Platform not configured" error
- Check that environment variables are set correctly
- Restart your backend after adding new variables
- Verify API keys are valid and have proper permissions

### "Access denied" error
- Ensure your access tokens haven't expired
- Check that tokens have the required permissions
- For Facebook, make sure you're using a Page Access Token, not a User Access Token

### Posts not appearing
- Check your social media accounts directly
- Verify the content meets platform guidelines
- Check for any error messages in the response

## 🔒 Security Best Practices

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Regularly rotate your access tokens
- Monitor your app's usage and permissions

## 📚 Additional Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)
- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [LinkedIn API Documentation](https://developer.linkedin.com/docs)

---

**Ready to start posting?** 🎉
Navigate to Dashboard → Publishing → Social Media and connect your first account!
