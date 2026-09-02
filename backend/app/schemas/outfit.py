from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.wardrobe import WardrobeItemResponse


class RecommendationRequest(BaseModel):
    occasion: Optional[str] = Field(None, description="Occasion name (e.g. casual, office, date, formal)")
    formality: Optional[float] = Field(None, ge=1.0, le=10.0, description="Target formality level")
    vibes: Optional[List[str]] = Field(default=None, description="Preferred style vibes to filter or boost")
    required_types: Optional[List[str]] = Field(
        default=None,
        description="List of specific types required in the outfit (e.g. ['shirt', 'pants', 'watch'])"
    )
    base_item: Optional[str] = Field(None, description="Base item name to build outfit around (for greedy suggestion)")
    strategy: Optional[str] = Field("best", description="Recommendation strategy: 'best', 'greedy', or 'random'")


class RecommendationResponse(BaseModel):
    strategy: str
    outfit: List[WardrobeItemResponse]
    score: Optional[float] = None
    breakdown: Optional[Dict[str, Any]] = None
    cached: bool = False
