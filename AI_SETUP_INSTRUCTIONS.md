# AI Insights Setup Instructions

This document provides instructions for setting up the AI insights functionality using LangChain and Gemini API.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account to access the Gemini API
2. **Python 3.8+**: Required for LangChain and related dependencies
3. **Database Access**: Ensure your database is running and accessible

## Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (it starts with "AIza...")

## Step 2: Configure Environment Variables

1. Navigate to the `backend` directory
2. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

3. Edit the `.env` file and add your Gemini API key:
   ```bash
   # AI Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   Replace `your_gemini_api_key_here` with the actual API key you obtained in Step 1.

## Step 3: Install Dependencies

1. Navigate to the `backend` directory
2. Install the new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `langchain==0.2.16`
   - `langchain-google-genai==0.1.11`
   - `langchain-community==0.2.16`

## Step 4: Start the Backend

1. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Verify the server is running by visiting `http://localhost:8000/docs`

## Step 5: Test the AI Functionality

### Test AI Analysis Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/ai-insights/analyze" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: your_user_id" \
  -d '{
    "include_competitors": true,
    "include_monitoring": true,
    "analysis_type": "comprehensive"
  }'
```

### Test AI Chat Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/ai-insights/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: your_user_id" \
  -d '{
    "message": "How are my campaigns performing?"
  }'
```

## Step 6: Frontend Integration

The frontend is already configured to use the AI endpoints. The following components are available:

1. **AI Insights Panel**: Located in the Optimization dashboard under the "AI Insights" tab
2. **Global AI Chat Widget**: Available as a floating chat button in the bottom-right corner

## Features

### AI Insights Panel
- **Scan Button**: Click to start AI analysis of your campaigns
- **Progress Bar**: Shows real-time progress during analysis
- **Results Display**: Shows performance score, insights, recommendations, and risk alerts
- **Actionable Recommendations**: Specific actions you can take to improve performance

### AI Chat Widget
- **Global Access**: Available on all pages
- **Quick Questions**: Pre-defined questions for common queries
- **Real-time Responses**: Get instant answers about your campaigns
- **Context Awareness**: AI has access to your campaign data, competitor info, and business documentation

## Data Sources

The AI agent has access to:

1. **Campaign Data**: From the `campaign_data` table
2. **Competitor Information**: From the `competitors` and `monitoring_data` tables
3. **Business Documentation**: README files in the project
4. **Real-time Monitoring**: Current monitoring data and alerts

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your Gemini API key is correctly set in the `.env` file
2. **Import Errors**: Make sure all dependencies are installed correctly
3. **Database Connection**: Verify your database is running and accessible
4. **CORS Issues**: Check that your frontend URL is in the allowed hosts

### Error Messages

- **"Failed to analyze campaigns"**: Check API key and database connection
- **"Unable to generate AI analysis"**: Verify LangChain dependencies are installed
- **"Authentication failed"**: Ensure user ID is being passed correctly

## Security Notes

1. **API Key Security**: Never commit your API key to version control
2. **Rate Limiting**: Be aware of Gemini API rate limits
3. **Data Privacy**: The AI processes your campaign data - ensure compliance with your data policies

## Performance Optimization

1. **Caching**: Consider implementing caching for repeated queries
2. **Batch Processing**: For large datasets, consider batch processing
3. **Async Processing**: The AI analysis is asynchronous to prevent blocking

## Support

If you encounter issues:

1. Check the backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test the API endpoints directly using curl or Postman
4. Ensure your database has the required tables and data

## Next Steps

After setup, you can:

1. Customize the AI prompts in `backend/app/services/ai_service.py`
2. Add more data sources for the AI to analyze
3. Implement caching for better performance
4. Add more specialized AI features for specific use cases
