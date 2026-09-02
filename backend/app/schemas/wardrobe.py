from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class WardrobeItemBase(BaseModel):
    item_name: str = Field(..., description="Unique name of the wardrobe item", example="Oxford White Shirt")
    type: str = Field(..., description="Item type (e.g., shirt, pants, shoes, watch, jacket)", example="shirt")
    category: Optional[str] = Field(None, description="Broad category (e.g., tops, bottoms, footwear, accessories)", example="tops")
    layer_index: int = Field(0, description="Layer index for 3D rendering and grouping (e.g. 0 for base, 1 for mid/outer)")
    color_name: Optional[str] = Field(None, description="Descriptive color name", example="white")

    reds: int = Field(0, ge=0, le=255, description="Red RGB channel (0-255)")
    green: int = Field(0, ge=0, le=255, description="Green RGB channel (0-255)")
    blue: int = Field(0, ge=0, le=255, description="Blue RGB channel (0-255)")
    hue: float = Field(0.0, ge=0.0, le=360.0, description="Hue degree on color wheel (0-360)")

    strap_reds: Optional[int] = Field(None, ge=0, le=255)
    strap_green: Optional[int] = Field(None, ge=0, le=255)
    strap_blue: Optional[int] = Field(None, ge=0, le=255)
    strap_hue: Optional[float] = Field(None, ge=0.0, le=360.0)

    dial_reds: Optional[int] = Field(None, ge=0, le=255)
    dial_green: Optional[int] = Field(None, ge=0, le=255)
    dial_blue: Optional[int] = Field(None, ge=0, le=255)
    dial_hue: Optional[float] = Field(None, ge=0.0, le=360.0)

    formality: float = Field(5.0, ge=1.0, le=10.0, description="Formality score 1 (very casual) to 10 (black tie)")
    vibe: List[str] = Field(default_factory=list, description="List of style vibe descriptors")


class WardrobeItemCreate(WardrobeItemBase):
    pass


class WardrobeItemUpdate(BaseModel):
    item_name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    layer_index: Optional[int] = None
    color_name: Optional[str] = None

    reds: Optional[int] = Field(None, ge=0, le=255)
    green: Optional[int] = Field(None, ge=0, le=255)
    blue: Optional[int] = Field(None, ge=0, le=255)
    hue: Optional[float] = Field(None, ge=0.0, le=360.0)

    strap_reds: Optional[int] = Field(None, ge=0, le=255)
    strap_green: Optional[int] = Field(None, ge=0, le=255)
    strap_blue: Optional[int] = Field(None, ge=0, le=255)
    strap_hue: Optional[float] = Field(None, ge=0.0, le=360.0)

    dial_reds: Optional[int] = Field(None, ge=0, le=255)
    dial_green: Optional[int] = Field(None, ge=0, le=255)
    dial_blue: Optional[int] = Field(None, ge=0, le=255)
    dial_hue: Optional[float] = Field(None, ge=0.0, le=360.0)

    formality: Optional[float] = Field(None, ge=1.0, le=10.0)
    vibe: Optional[List[str]] = None


class WardrobeItemResponse(WardrobeItemBase):
    id: int
    color_vec: Optional[List[int]] = None
    strap_color_vec: Optional[List[int]] = None
    dial_color_vec: Optional[List[int]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
