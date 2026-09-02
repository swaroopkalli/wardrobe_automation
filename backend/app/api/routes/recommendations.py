from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.outfit import RecommendationRequest, RecommendationResponse
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Outfit Recommendations"])


@router.post("", response_model=RecommendationResponse, summary="Get structured outfit recommendation")
def get_recommendation(req: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Generate an outfit recommendation based on structured criteria,
    using the optimized Stage 1 branch-and-bound engine and Redis cache.
    """
    service = RecommendationService(db)
    return service.recommend(req)
