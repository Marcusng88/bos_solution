from pydantic import BaseModel, Field
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
    
    model_config = {
        "from_attributes": True
    }
