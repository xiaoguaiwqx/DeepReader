from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class Paper(BaseModel):
    """
    Represents a research paper from ArXiv or other sources.
    """
    arxiv_id: str = Field(..., description="Unique ID from ArXiv (e.g., 2301.12345)")
    title: str
    authors: List[str]
    summary: str
    published_date: datetime
    updated_date: datetime
    primary_category: str
    categories: List[str]
    pdf_url: Optional[str] = None
    
    model_config = ConfigDict(frozen=True)
