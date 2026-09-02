from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.wardrobe import (
    WardrobeItemCreate,
    WardrobeItemUpdate,
    WardrobeItemResponse
)
from app.services.wardrobe import WardrobeService
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe Items"])


@router.get("/items", response_model=List[WardrobeItemResponse], summary="List all wardrobe items")
def list_items(
    item_type: Optional[str] = Query(None, alias="type", description="Filter by item type (e.g. shirt, pants, watch)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. tops, bottoms)"),
    db: Session = Depends(get_db)
):
    """Retrieve all wardrobe items, with optional filtering by type or category."""
    service = WardrobeService(db)
    return service.get_items(item_type=item_type, category=category)


@router.get("/items/{item_id}", response_model=WardrobeItemResponse, summary="Get wardrobe item by ID")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single wardrobe item by its unique ID."""
    service = WardrobeService(db)
    item = service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wardrobe item with id {item_id} not found"
        )
    return item


@router.post("/items", response_model=WardrobeItemResponse, status_code=status.HTTP_201_CREATED, summary="Create wardrobe item")
def create_item(item_in: WardrobeItemCreate, db: Session = Depends(get_db)):
    """Create a new wardrobe item in the database."""
    service = WardrobeService(db)
    created = service.create_item(item_in)
    RecommendationService.invalidate_in_memory_engine()
    return created


@router.put("/items/{item_id}", response_model=WardrobeItemResponse, summary="Update wardrobe item")
def update_item(item_id: int, item_in: WardrobeItemUpdate, db: Session = Depends(get_db)):
    """Update an existing wardrobe item."""
    service = WardrobeService(db)
    updated = service.update_item(item_id, item_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wardrobe item with id {item_id} not found"
        )
    RecommendationService.invalidate_in_memory_engine()
    return updated


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete wardrobe item")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a wardrobe item from the database."""
    service = WardrobeService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wardrobe item with id {item_id} not found"
        )
    RecommendationService.invalidate_in_memory_engine()
    return None
