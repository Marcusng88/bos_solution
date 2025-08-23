# ROI Report Generator Troubleshooting Guide

## Common Issues and Solutions

### 1. 500 Internal Server Error

**Symptoms:**
- Frontend shows "Failed to generate report"
- Backend logs show 500 error
- API endpoint returns 500 status

**Possible Causes and Solutions:**

#### A. Gemini API Key Not Configured
```
Error: "Gemini API key not configured"
```

**Solution:**
1. Add `GEMINI_API_KEY` to your `.env` file
2. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Restart the backend server

#### B. Supabase Connection Issues
```
Error: "Failed to fetch ROI metrics data"
```

**Solution:**
1. Verify Supabase credentials in `.env`:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```
2. Check if the `roi_metrics` table exists
3. Verify network connectivity

#### C. Database Table Issues
```
Error: "relation 'roi_metrics' does not exist"
```

**Solution:**
1. Run the database schema setup:
   ```bash
   cd backend
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```
2. Or manually create the table using the SQL in `app/core/ROI backend/roi/sql/01_roi_schema.sql`

### 2. No Data Available

**Symptoms:**
- Report generates but shows "No ROI Data Available"
- Empty report sections
- No platform data displayed

**Solutions:**

#### A. Add Sample Data
Run the sample data script:
```bash
cd backend
python add_sample_roi_data.py
```

#### B. Check Data Time Range
The report generator looks for data in:
- Current month (from 1st of current month to now)
- Previous month (from 1st of previous month to end of previous month)

If your data is outside this range, it won't be included.

#### C. Verify Data Structure
Ensure your `roi_metrics` table has the correct structure:
```sql
CREATE TABLE IF NOT EXISTS roi_metrics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    views INTEGER DEFAULT 1,
    likes INTEGER DEFAULT 1,
    comments INTEGER DEFAULT 1,
    shares INTEGER DEFAULT 1,
    clicks INTEGER DEFAULT 1,
    ad_spend DECIMAL(10,2) DEFAULT 0.00,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    roi_percentage DECIMAL(8,2) DEFAULT 0.00,
    update_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Gemini API Errors

**Symptoms:**
- "Gemini API error" in logs
- Timeout errors
- Rate limit errors

**Solutions:**

#### A. Check API Key
1. Verify the API key is correct
2. Ensure the key has proper permissions
3. Check if the key is expired

#### B. Rate Limits
If you hit rate limits:
1. Wait a few minutes before retrying
2. Consider upgrading your Gemini API plan
3. Implement retry logic with exponential backoff

#### C. Model Availability
The system uses `gemini-1.5-flash`. If this model is unavailable:
1. Check Google AI Studio for model status
2. Consider switching to `gemini-pro` as fallback

### 4. Frontend Issues

**Symptoms:**
- Button doesn't respond
- Loading state stuck
- Error messages not displayed

**Solutions:**

#### A. Check Network Requests
1. Open browser developer tools
2. Go to Network tab
3. Click "Generate Report"
4. Check if the request is made and what response is received

#### B. Console Errors
1. Check browser console for JavaScript errors
2. Look for CORS issues
3. Verify API endpoint URL is correct

#### C. Authentication Issues
1. Ensure user is logged in
2. Check if Clerk authentication is working
3. Verify user ID is being passed correctly

## Testing Steps

### 1. Test Backend Directly
```bash
cd backend
python test_endpoint.py
```

### 2. Test Database Connection
```bash
cd backend
python test_report_generator.py
```

### 3. Test with Sample Data
```bash
cd backend
python add_sample_roi_data.py
```

### 4. Test Frontend
1. Start the frontend development server
2. Navigate to `/dashboard/roi/reports`
3. Click "Generate Report"
4. Check for any errors in browser console

## Debug Mode

Enable detailed logging by setting:
```bash
LOG_LEVEL=DEBUG
```

This will show:
- Database query details
- API request/response logs
- Error stack traces
- Data processing steps

## Common Error Messages

### Backend Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Gemini API key not configured" | Missing environment variable | Add GEMINI_API_KEY to .env |
| "Failed to fetch ROI metrics data" | Database connection issue | Check Supabase credentials |
| "relation 'roi_metrics' does not exist" | Missing table | Run database setup |
| "generate_ai_report failed" | General processing error | Check logs for details |

### Frontend Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Failed to generate report" | API call failed | Check backend logs |
| "Please log in to generate reports" | Authentication issue | Ensure user is logged in |
| "No ROI Data Available" | No data in database | Add sample data or check time range |

## Performance Issues

### Slow Report Generation
1. **Large datasets**: Consider implementing pagination
2. **Gemini API delays**: Add timeout handling
3. **Database queries**: Optimize with indexes

### Memory Issues
1. **Large data processing**: Process data in chunks
2. **Report size**: Limit data volume for reports

## Environment Variables Checklist

Ensure these are set in your `.env` file:

```bash
# Required for report generation
GEMINI_API_KEY=your_gemini_api_key_here

# Required for database access
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Optional for debugging
LOG_LEVEL=DEBUG
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look for detailed error messages
2. **Run test scripts**: Use the provided test scripts to isolate issues
3. **Verify setup**: Ensure all dependencies and environment variables are correct
4. **Check documentation**: Review the main ROI_REPORT_GENERATOR.md file

## Quick Fix Checklist

- [ ] Gemini API key configured
- [ ] Supabase credentials correct
- [ ] Database table exists
- [ ] Sample data added (if testing)
- [ ] Backend server running
- [ ] Frontend server running
- [ ] User logged in
- [ ] No console errors
- [ ] Network requests successful
