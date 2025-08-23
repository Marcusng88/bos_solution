# BOS Solution Backend

Business Operations System - Continuous Monitoring and Competitor Intelligence Backend API

## Overview

This backend provides a RESTful API for the BOS Solution platform, handling competitor intelligence, continuous monitoring, user management, and AI-powered insights. The backend is designed to work with a Clerk-authenticated frontend and stores all data directly in Supabase using the REST API.

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: Direct PostgreSQL database integration via REST API
- **LangChain**: AI framework for intelligent analysis and recommendations
- **Gemini API**: Google's AI model for natural language processing
- **Authentication**: Header-based user identification (frontend handles Clerk auth)
- **No Local Database**: All data operations go directly to Supabase

## Key Changes (Latest Update)

- **Removed SQLAlchemy**: No more local database models or ORM
- **Direct Supabase Integration**: All database operations use Supabase REST API
- **Simplified Architecture**: Cleaner, more maintainable codebase
- **Better Performance**: No local database overhead

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
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=true

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Social Media API Keys
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here

# AI Service Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bos_solution/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Test the application**
   ```bash
   python test_app.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## API Endpoints

### Authentication
- `GET /api/v1/auth/verify` - Verify user authentication
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/sync` - Sync user data from Clerk

### Users
- `GET /api/v1/users/profile` - Get user profile
- `GET /api/v1/users/settings` - Get user monitoring settings
- `PUT /api/v1/users/settings` - Update user monitoring settings
- `GET /api/v1/users/preferences` - Get user preferences
- `PUT /api/v1/users/preferences` - Update user preferences

### Competitors
- `GET /api/v1/competitors/` - Get all competitors
- `GET /api/v1/competitors/{id}` - Get specific competitor
- `POST /api/v1/competitors/` - Create new competitor
- `PUT /api/v1/competitors/{id}` - Update competitor
- `DELETE /api/v1/competitors/{id}` - Delete competitor
- `POST /api/v1/competitors/{id}/scan` - Trigger competitor scan

### Monitoring
- `GET /api/v1/monitoring/data/{competitor_id}` - Get monitoring data
- `POST /api/v1/monitoring/data` - Create monitoring data
- `GET /api/v1/monitoring/alerts` - Get monitoring alerts
- `POST /api/v1/monitoring/alerts` - Create monitoring alert
- `GET /api/v1/monitoring/stats/{competitor_id}` - Get monitoring statistics

## Database Schema

The application expects the following tables in Supabase:

- `users` - User information synced from Clerk
- `competitors` - Competitor monitoring targets
- `monitoring_data` - Social media monitoring results
- `monitoring_alerts` - Monitoring alerts and notifications
- `user_monitoring_settings` - User monitoring preferences
- `user_preferences` - User onboarding and preference data

## Development

### Testing
```bash
# Run the test script
python test_app.py

# Run the application
python main.py
```

### Code Structure
```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core configuration and utilities
│   ├── schemas/       # Pydantic data models
│   └── services/      # Business logic services
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── test_app.py        # Test script
```

## Troubleshooting

### Common Issues

1. **Supabase Connection Failed**
   - Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`
   - Verify Supabase project is active and accessible

2. **Enum Error for 'website' Platform**
   - Run the enum fix script: `python fix_enum_issue.py`
   - Or manually add the value in Supabase dashboard

3. **Authentication Errors**
   - Ensure `X-User-ID` header is sent with all requests
   - Verify Clerk authentication is working on frontend

### Getting Help

- Check the logs for detailed error messages
- Verify environment variables are set correctly
- Test individual components with the test script

## License

This project is part of the Future Ready Hackathon 2025.
