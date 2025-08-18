# BOS Solution Backend

Business Operations System - Continuous Monitoring and Competitor Intelligence Backend API

## Overview

This backend provides a RESTful API for the BOS Solution platform, handling competitor intelligence, continuous monitoring, user management, and AI-powered insights. The backend is designed to work with a Clerk-authenticated frontend and stores all data in Supabase.

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **Supabase**: PostgreSQL database with real-time capabilities
- **LangChain**: AI framework for intelligent analysis and recommendations
- **Gemini API**: Google's AI model for natural language processing
- **Authentication**: Header-based user identification (frontend handles Clerk auth)

## AI Features

The backend includes advanced AI capabilities powered by LangChain and Google's Gemini API:

### AI Insights
- **Campaign Analysis**: Intelligent analysis of campaign performance data
- **Recommendations**: Actionable optimization suggestions
- **Risk Assessment**: Automated risk detection and mitigation strategies
- **Competitive Intelligence**: AI-powered competitor analysis

### AI Chat Assistant
- **Natural Language Queries**: Ask questions about campaigns in plain English
- **Context Awareness**: AI has access to campaign data, competitor info, and business documentation
- **Real-time Responses**: Instant answers to business questions
- **Global Availability**: Available across all application pages

## Authentication

The backend uses a simple header-based authentication system:

- **Frontend Responsibility**: Clerk handles all authentication, login, and user management
- **Backend Integration**: Frontend sends `X-User-ID` header with each request
- **Security**: User ID is extracted from headers and used for data isolation

### How It Works

1. User authenticates with Clerk on the frontend
2. Frontend extracts user ID from Clerk session
3. Frontend sends `X-User-ID` header with all API requests
4. Backend validates the header and uses the user ID for data operations
5. All data is automatically scoped to the authenticated user

### Example Request

```bash
curl -H "X-User-ID: user_123" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/v1/users/settings
```

## Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/bos_solution
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Social Media API Keys
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here

# Monitoring Settings
DEFAULT_SCAN_FREQUENCY=60
MAX_CONCURRENT_SCANS=5

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379
```

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your actual values
```

4. Run the application:
```bash
python -m uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `GET /api/v1/auth/verify` - Verify user ID from header
- `GET /api/v1/auth/me` - Get current user information

### Users
- `GET /api/v1/users/settings` - Get user monitoring settings
- `PUT /api/v1/users/settings` - Update user monitoring settings

### Competitors
- `GET /api/v1/competitors/` - Get all competitors
- `POST /api/v1/competitors/` - Create a new competitor
- `GET /api/v1/competitors/{id}` - Get specific competitor
- `PUT /api/v1/competitors/{id}` - Update competitor
- `DELETE /api/v1/competitors/{id}` - Delete competitor
- `GET /api/v1/competitors/{id}/analysis` - Get competitor analysis
- `POST /api/v1/competitors/{id}/analysis` - Create competitor analysis

### Monitoring
- `GET /api/v1/monitoring/sessions` - Get monitoring sessions
- `POST /api/v1/monitoring/sessions` - Create monitoring session
- `GET /api/v1/monitoring/sessions/{id}` - Get specific session
- `PUT /api/v1/monitoring/sessions/{id}` - Update session
- `DELETE /api/v1/monitoring/sessions/{id}` - Delete session
- `GET /api/v1/monitoring/alerts` - Get monitoring alerts
- `POST /api/v1/monitoring/alerts` - Create monitoring alert
- `PUT /api/v1/monitoring/alerts/{id}/read` - Mark alert as read

### AI Insights
- `POST /api/v1/ai-insights/analyze` - Analyze campaigns and generate AI insights
- `POST /api/v1/ai-insights/chat` - Chat with AI about campaigns and business questions
- `GET /api/v1/ai-insights/insights` - Get AI insights for campaigns

### Self-Optimization
- `GET /api/v1/self-optimization/dashboard/metrics` - Get dashboard metrics
- `GET /api/v1/self-optimization/campaigns` - Get campaign data
- `GET /api/v1/self-optimization/overspending-predictions` - Get overspending predictions
- `PUT /api/v1/self-optimization/campaigns/status` - Update campaign status
- `PUT /api/v1/self-optimization/campaigns/budget` - Update campaign budget
- `GET /api/v1/self-optimization/alerts` - Get optimization alerts
- `GET /api/v1/self-optimization/risk-patterns` - Get risk patterns
- `GET /api/v1/self-optimization/recommendations` - Get optimization recommendations

## Frontend Integration

### Setting User ID Header

In your frontend application, after Clerk authentication:

```typescript
// After successful Clerk authentication
const { user } = useUser();

// Set up axios or fetch with default headers
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'X-User-ID': user?.id || '',
    'Content-Type': 'application/json'
  }
});

// Or for individual requests
fetch('/api/v1/users/settings', {
  headers: {
    'X-User-ID': user.id,
    'Content-Type': 'application/json'
  }
});
```

### Error Handling

The backend will return `401 Unauthorized` if the `X-User-ID` header is missing or invalid. Handle this in your frontend:

```typescript
try {
  const response = await api.get('/users/settings');
  // Handle success
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login or refresh Clerk session
    await signIn();
  }
}
```

## AI Setup

For detailed AI setup instructions, see [AI_SETUP_INSTRUCTIONS.md](../AI_SETUP_INSTRUCTIONS.md).

### Quick AI Setup

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add the key to your `.env` file:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Restart the backend server

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8
```

## Database Schema

The application uses SQLAlchemy models with automatic table creation. Key tables include:

- `user_monitoring_settings` - User preferences and configuration
- `competitors` - Competitor information and metadata
- `competitor_analyses` - Analysis results for competitors
- `monitoring_sessions` - Active monitoring sessions
- `monitoring_alerts` - Generated alerts and notifications
- `campaign_data` - Campaign performance data for AI analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Future Ready Hackathon 2025.
