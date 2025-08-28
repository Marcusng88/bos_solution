# AI Agent Invocation in Content Planning

## Overview
The AI agent in the content planning system is designed to be **explicitly invoked by user actions** rather than running automatically. This ensures optimal performance and user control.

## How It Works

### 1. Dashboard Loading (Automatic)
- **What happens**: Basic dashboard data, supported options, and industry information are loaded automatically when the page loads
- **What does NOT happen**: The AI agent is NOT invoked during this process
- **Purpose**: Provides a responsive user interface with basic information

### 2. AI Agent Invocation (Manual Only)
The AI agent is **ONLY** invoked when the user explicitly performs one of these actions:

#### A. Create Content Button
- **Location**: Main dashboard header, "Create Content" button
- **Action**: Opens the AI Content Generator modal
- **AI Invocation**: Only happens when user clicks "Generate Content" button inside the modal
- **What it does**: Generates social media content based on user specifications

#### B. Other AI Functions (When Available)
- **Competitor Analysis**: Only when user explicitly requests competitor analysis
- **Hashtag Research**: Only when user explicitly requests hashtag research
- **Strategy Generation**: Only when user explicitly requests strategy generation
- **Content Calendar**: Only when user explicitly requests calendar generation
- **Gap Analysis**: Only when user explicitly requests gap identification

## Code Structure

### Content Planning Dashboard
```tsx
// Only loads basic data, doesn't invoke AI
const { dashboardData, supportedOptions, loading, error } = useContentPlanning({ 
  industry: 'technology', 
  autoLoad: true // This only loads basic dashboard data, not AI agent
})
```

### AI Content Generator
```tsx
// AI agent is ONLY invoked when user clicks "Generate Content" button
const handleGenerate = async () => {
  // ... form validation ...
  
  // AI agent is invoked here - only when user explicitly requests it
  const response = await generateContent(requestData)
  setGeneratedContent(response.content)
}
```

## Benefits of This Approach

1. **Performance**: No unnecessary AI processing on page load
2. **Cost Control**: AI API calls only happen when needed
3. **User Control**: Users decide when to use AI features
4. **Responsiveness**: Dashboard loads quickly with basic data
5. **Transparency**: Clear indication of when AI is being used

## User Experience Flow

1. **Page Load**: Dashboard loads with basic stats and information
2. **User Action**: User clicks "Create Content" button
3. **Modal Opens**: AI Content Generator modal appears
4. **User Input**: User fills out content requirements
5. **AI Invocation**: User clicks "Generate Content" button
6. **AI Processing**: AI agent generates content based on specifications
7. **Results Display**: Generated content is shown to user

## Configuration

The system can be configured to change this behavior if needed:

```tsx
// Current behavior (recommended)
const { data } = useContentPlanning({ autoLoad: true })

// Alternative: No auto-loading at all
const { data } = useContentPlanning({ autoLoad: false })

// Alternative: Load everything including AI analysis
// (This would require modifying the hook to include AI functions in autoLoad)
```

## Summary

- ✅ **Dashboard loads automatically** with basic data
- ❌ **AI agent does NOT run automatically**
- ✅ **AI agent runs ONLY when user explicitly requests it**
- ✅ **Clear user control** over when AI features are used
- ✅ **Optimal performance** and cost management

This design ensures that users have full control over when the AI agent is invoked while maintaining a responsive and informative dashboard experience.
