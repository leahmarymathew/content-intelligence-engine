from pydantic import BaseModel
from typing import Optional, Dict, Any


class ContentResponse(BaseModel):
    """Response model for generated content"""
    id: Optional[int] = None
    title: str
    summary: str
    content: str
    category: Optional[str] = None
    metadata: Dict[str, Any]


class ContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str
    audience: str
    tone: str
    contentType: Optional[str] = None
