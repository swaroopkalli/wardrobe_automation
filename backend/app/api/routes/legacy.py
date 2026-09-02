from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.wardrobe import WardrobeItemResponse
from app.schemas.outfit import RecommendationRequest
from app.services.wardrobe import WardrobeService
from app.services.recommendation import RecommendationService

router = APIRouter(tags=["Legacy & Compatibility"])


@router.get("/items", response_model=List[WardrobeItemResponse], summary="Legacy /items endpoint")
def legacy_get_items(db: Session = Depends(get_db)):
    service = WardrobeService(db)
    return service.get_items()


@router.get("/items/{item_type}", response_model=List[WardrobeItemResponse], summary="Legacy /items/<type> endpoint")
def legacy_get_items_by_type(item_type: str, db: Session = Depends(get_db)):
    service = WardrobeService(db)
    return service.get_items(item_type=item_type)


@router.get("/suggest/{item_name}", summary="Legacy /suggest/<item_name> endpoint")
def legacy_suggest(item_name: str, db: Session = Depends(get_db)):
    service = RecommendationService(db)
    req = RecommendationRequest(strategy="greedy", base_item=item_name)
    rec = service.recommend(req)
    return {
        "base_item": item_name,
        "outfit": [it["item_name"] for it in rec["outfit"]]
    }


@router.get("/best", summary="Legacy /best endpoint")
def legacy_best_outfit(db: Session = Depends(get_db)):
    service = RecommendationService(db)
    req = RecommendationRequest(strategy="best", required_types=["shirt", "pants", "watch"])
    rec = service.recommend(req)
    return {
        "outfit": [it["item_name"] for it in rec["outfit"]],
        "score": rec["score"]
    }


@router.get("/random/{item_name}", summary="Legacy /random/<item_name> endpoint")
def legacy_random(item_name: str, db: Session = Depends(get_db)):
    service = RecommendationService(db)
    req = RecommendationRequest(strategy="random", base_item=item_name)
    rec = service.recommend(req)
    return {
        "start_item": item_name,
        "outfit": [it["item_name"] for it in rec["outfit"]]
    }


@router.get("/graph/stats", summary="Legacy /graph/stats endpoint")
def legacy_graph_stats(db: Session = Depends(get_db)):
    service = RecommendationService(db)
    service._ensure_engine()
    g = RecommendationService._cached_graph
    return {
        "nodes": g.number_of_nodes() if g else 0,
        "edges": g.number_of_edges() if g else 0
    }
