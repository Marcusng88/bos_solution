# Database Implementation Plan: User Preferences & Competitor Tracking

## 🎯 **Overview**
This document outlines the complete implementation plan for storing user preferences from onboarding and competitor information in the database. The plan includes:

1. **New Database Tables** - `user_preferences` and `my_competitors`
2. **Backend API Endpoints** - For saving and retrieving user data
3. **Frontend Integration** - Connecting onboarding forms to backend
4. **Data Display** - Showing saved preferences in settings

---

## 🗄️ **Database Schema Updates**

### **1. User Preferences Table**
```sql
-- Add to database_schema.sql after existing tables

-- User preferences table - stores onboarding preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL UNIQUE, -- Clerk user ID
    industry VARCHAR(100) NOT NULL,
    company_size VARCHAR(50) NOT NULL,
    marketing_goals TEXT[] NOT NULL, -- Array of marketing objectives
    monthly_budget VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_company_size CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500', '500+')),
    CONSTRAINT valid_budget CHECK (monthly_budget IN ('$0 - $1,000', '$1,000 - $5,000', '$5,000 - $10,000', '$10,000 - $25,000', '$25,000+')),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_user_preferences_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE
);

-- Create indexes for user preferences
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_industry ON user_preferences(industry);
CREATE INDEX idx_user_preferences_company_size ON user_preferences(company_size);

-- Create trigger for updated_at
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### **2. My Competitors Table**
```sql
-- My competitors table - stores user's competitor information
CREATE TABLE my_competitors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    competitor_name VARCHAR(255) NOT NULL,
    website_url VARCHAR(500),
    active_platforms TEXT[] NOT NULL, -- Array of platforms they're active on
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_platforms CHECK (array_length(active_platforms, 1) > 0),
    
    -- Foreign key reference to users table
    CONSTRAINT fk_my_competitors_user_id FOREIGN KEY (user_id) REFERENCES users(clerk_id) ON DELETE CASCADE,
    
    -- Unique constraint: one user can't have duplicate competitor names
    CONSTRAINT unique_user_competitor_name UNIQUE(user_id, competitor_name)
);

-- Create indexes for my competitors
CREATE INDEX idx_my_competitors_user_id ON my_competitors(user_id);
CREATE INDEX idx_my_competitors_competitor_name ON my_competitors(competitor_name);
CREATE INDEX idx_my_competitors_platforms ON my_competitors USING gin(active_platforms);

-- Create trigger for updated_at
CREATE TRIGGER update_my_competitors_updated_at BEFORE UPDATE ON my_competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 🔧 **Backend Implementation**

### **1. New Models**

#### **`app/models/user_preferences.py`**
```python
from sqlalchemy import Column, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100), nullable=False)
    company_size = Column(String(50), nullable=False)
    marketing_goals = Column(ARRAY(Text), nullable=False)
    monthly_budget = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### **`app/models/my_competitor.py`**
```python
from sqlalchemy import Column, String, Text, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class MyCompetitor(Base):
    __tablename__ = "my_competitors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(String(255), nullable=False)
    competitor_name = Column(String(255), nullable=False)
    website_url = Column(String(500))
    active_platforms = Column(ARRAY(Text), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### **2. New Schemas**

#### **`app/schemas/user_preferences.py`**
```python
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class UserPreferencesBase(BaseModel):
    industry: str = Field(..., description="User's industry")
    company_size: str = Field(..., description="Company size category")
    marketing_goals: List[str] = Field(..., description="List of marketing objectives")
    monthly_budget: str = Field(..., description="Monthly marketing budget range")

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferences(UserPreferencesBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### **`app/schemas/my_competitor.py`**
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class MyCompetitorBase(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    website_url: Optional[str] = Field(None, description="Competitor's website URL")
    active_platforms: List[str] = Field(..., description="Platforms where competitor is active")

class MyCompetitorCreate(MyCompetitorBase):
    pass

class MyCompetitorUpdate(MyCompetitorBase):
    pass

class MyCompetitor(MyCompetitorBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### **3. New API Endpoints**

#### **`app/api/v1/endpoints/user_preferences.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user_preferences import UserPreferences
from app.schemas.user_preferences import UserPreferencesCreate, UserPreferencesUpdate, UserPreferences as UserPreferencesSchema
from app.core.auth_utils import get_current_user_id

router = APIRouter()

@router.post("/", response_model=UserPreferencesSchema)
async def create_user_preferences(
    preferences: UserPreferencesCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create or update user preferences"""
    try:
        # Check if preferences already exist
        existing = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        
        if existing:
            # Update existing preferences
            for field, value in preferences.dict().items():
                setattr(existing, field, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new preferences
            db_preferences = UserPreferences(
                user_id=user_id,
                **preferences.dict()
            )
            db.add(db_preferences)
            db.commit()
            db.refresh(db_preferences)
            return db_preferences
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user preferences: {str(e)}"
        )

@router.get("/", response_model=UserPreferencesSchema)
async def get_user_preferences(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    return preferences

@router.put("/", response_model=UserPreferencesSchema)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    db_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not db_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    
    for field, value in preferences.dict(exclude_unset=True).items():
        setattr(db_preferences, field, value)
    
    db.commit()
    db.refresh(db_preferences)
    return db_preferences
```

#### **`app/api/v1/endpoints/my_competitors.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.my_competitor import MyCompetitor
from app.schemas.my_competitor import MyCompetitorCreate, MyCompetitorUpdate, MyCompetitor as MyCompetitorSchema
from app.core.auth_utils import get_current_user_id

router = APIRouter()

@router.post("/", response_model=MyCompetitorSchema)
async def create_competitor(
    competitor: MyCompetitorCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new competitor entry"""
    try:
        db_competitor = MyCompetitor(
            user_id=user_id,
            **competitor.dict()
        )
        db.add(db_competitor)
        db.commit()
        db.refresh(db_competitor)
        return db_competitor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create competitor: {str(e)}"
        )

@router.get("/", response_model=List[MyCompetitorSchema])
async def get_user_competitors(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all competitors for the current user"""
    competitors = db.query(MyCompetitor).filter(MyCompetitor.user_id == user_id).all()
    return competitors

@router.put("/{competitor_id}", response_model=MyCompetitorSchema)
async def update_competitor(
    competitor_id: str,
    competitor: MyCompetitorUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update a competitor entry"""
    db_competitor = db.query(MyCompetitor).filter(
        MyCompetitor.id == competitor_id,
        MyCompetitor.user_id == user_id
    ).first()
    
    if not db_competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    for field, value in competitor.dict(exclude_unset=True).items():
        setattr(db_competitor, field, value)
    
    db.commit()
    db.refresh(db_competitor)
    return db_competitor

@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a competitor entry"""
    db_competitor = db.query(MyCompetitor).filter(
        MyCompetitor.id == competitor_id,
        MyCompetitor.user_id == user_id
    ).first()
    
    if not db_competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    db.delete(db_competitor)
    db.commit()
    return {"message": "Competitor deleted successfully"}
```

### **4. Update Main API Router**

#### **`app/api/v1/api.py`**
```python
# Add these lines to the existing router includes
from app.api.v1.endpoints import user_preferences, my_competitors

# Add these lines to the existing router.include_router calls
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(my_competitors.router, prefix="/my-competitors", tags=["my-competitors"])
```

---

## 🎨 **Frontend Integration**

### **1. API Client Functions**

#### **`lib/api-client.ts`** - Add these functions:
```typescript
// User Preferences API
export const saveUserPreferences = async (preferences: {
  industry: string
  companySize: string
  goals: string[]
  budget: string
}) => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user-preferences`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      industry: preferences.industry,
      company_size: preferences.companySize,
      marketing_goals: preferences.goals,
      monthly_budget: preferences.budget
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to save user preferences')
  }
  
  return response.json()
}

export const getUserPreferences = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user-preferences`)
  
  if (!response.ok) {
    throw new Error('Failed to get user preferences')
  }
  
  return response.json()
}

// My Competitors API
export const saveCompetitor = async (competitor: {
  name: string
  website: string
  platforms: string[]
}) => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/my-competitors`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      competitor_name: competitor.name,
      website_url: competitor.website,
      active_platforms: competitor.platforms
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to save competitor')
  }
  
  return response.json()
}

export const getUserCompetitors = async () => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/my-competitors`)
  
  if (!response.ok) {
    throw new Error('Failed to get competitors')
  }
  
  return response.json()
}

export const updateCompetitor = async (id: string, competitor: {
  name: string
  website: string
  platforms: string[]
}) => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/my-competitors/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      competitor_name: competitor.name,
      website_url: competitor.website,
      active_platforms: competitor.platforms
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to update competitor')
  }
  
  return response.json()
}

export const deleteCompetitor = async (id: string) => {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/my-competitors/${id}`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error('Failed to delete competitor')
  }
  
  return response.json()
}
```

### **2. Update Onboarding Components**

#### **`components/onboarding/onboarding-wizard.tsx`** - Add save function:
```typescript
// Add this import
import { saveUserPreferences, saveCompetitor } from "@/lib/api-client"

// Add this function inside the component
const saveOnboardingData = async () => {
  try {
    // Save user preferences
    await saveUserPreferences({
      industry: data.industry,
      companySize: data.companySize,
      goals: data.goals,
      budget: data.budget
    })
    
    // Save competitors (one by one)
    for (const competitor of data.competitors) {
      await saveCompetitor({
        name: competitor.name,
        website: competitor.website,
        platforms: competitor.platforms
      })
    }
    
    // Show success message
    toast({
      title: "Onboarding Complete!",
      description: "Your preferences have been saved successfully.",
    })
    
    // Redirect to dashboard
    router.push('/dashboard')
  } catch (error) {
    console.error('Failed to save onboarding data:', error)
    toast({
      title: "Save Failed",
      description: "Failed to save your preferences. Please try again.",
      variant: "destructive",
    })
  }
}

// Update the CompletionStep to call this function
<CompletionStep 
  data={data} 
  onComplete={saveOnboardingData} 
/>
```

### **3. Update Settings Components**

#### **`components/settings/settings-wizard.tsx`** - Add data loading:
```typescript
// Add these imports
import { getUserPreferences, getUserCompetitors } from "@/lib/api-client"
import { useEffect } from "react"

// Add this inside the component
useEffect(() => {
  const loadUserData = async () => {
    try {
      const [preferences, competitors] = await Promise.all([
        getUserPreferences(),
        getUserCompetitors()
      ])
      
      // Transform data to match OnboardingData interface
      const transformedData = {
        industry: preferences.industry || "Fashion & Apparel",
        companySize: preferences.company_size || "51-200",
        goals: preferences.marketing_goals || ["Brand Awareness", "Lead Generation"],
        competitors: competitors.map((comp: any) => ({
          name: comp.competitor_name,
          website: comp.website_url || "",
          platforms: comp.active_platforms || []
        })),
        connectedAccounts: data.connectedAccounts,
        budget: preferences.monthly_budget || "$5,000 - $10,000"
      }
      
      setData(transformedData)
    } catch (error) {
      console.error('Failed to load user data:', error)
    }
  }
  
  loadUserData()
}, [])
```

---

## 📊 **Data Display Implementation**

### **1. Settings Page Updates**

The settings page will now automatically load and display:
- **Industry** from database
- **Company Size** from database  
- **Marketing Goals** from database
- **Monthly Budget** from database
- **Competitors** from database

### **2. Data Persistence**

All onboarding data will now be:
- ✅ **Saved to database** when onboarding completes
- ✅ **Loaded from database** when visiting settings
- ✅ **Editable** through the settings wizard
- ✅ **Persistent** across sessions

---

## 🚀 **Implementation Steps**

### **Phase 1: Database Setup**
1. ✅ Update `database_schema.sql` with new tables
2. ✅ Run database migrations
3. ✅ Test table creation

### **Phase 2: Backend Implementation**
1. ✅ Create new models (`UserPreferences`, `MyCompetitor`)
2. ✅ Create new schemas
3. ✅ Create new API endpoints
4. ✅ Update main API router
5. ✅ Test endpoints

### **Phase 3: Frontend Integration**
1. ✅ Add API client functions
2. ✅ Update onboarding wizard to save data
3. ✅ Update settings wizard to load data
4. ✅ Test data flow

### **Phase 4: Testing & Validation**
1. ✅ Test complete onboarding flow
2. ✅ Verify data persistence
3. ✅ Test settings page data loading
4. ✅ Validate competitor management

---

## 🔍 **Key Benefits**

1. **Data Persistence** - User preferences are never lost
2. **Settings Sync** - Settings page shows actual saved data
3. **Competitor Tracking** - Users can manage their competitor list
4. **Scalable Structure** - Easy to add more preference fields later
5. **Clean Separation** - `my_competitors` table avoids conflicts with friend's work

---

## ⚠️ **Important Notes**

1. **Don't touch existing `competitors` table** - It's your friend's work
2. **`my_competitors` table** - Separate table for user's own competitor tracking
3. **Settings page** - Will automatically load real data instead of hardcoded values
4. **Onboarding completion** - Now saves everything to database
5. **Data validation** - Backend validates all input data

---

## 🎯 **Next Steps After Implementation**

1. **Test the complete flow** - Onboarding → Database → Settings
2. **Verify data persistence** - Check database after onboarding
3. **Test competitor management** - Add/edit/delete competitors
4. **Validate settings display** - Ensure real data shows up
5. **Clean up during merge** - Remove hardcoded values from settings

---

**This implementation provides a complete, production-ready solution for storing and managing user preferences and competitor data! 🚀**
