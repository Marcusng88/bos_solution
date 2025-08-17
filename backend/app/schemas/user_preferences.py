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
    
    model_config = {
        "from_attributes": True
    }
