import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend is in path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.db.database import Base, get_db
from app.main import app
from app.models.wardrobe import WardrobeItem
from app.cache.redis import cache_client
from app.services.recommendation import RecommendationService
from scripts.import_csv import import_csv_to_postgres

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    # Populate sample items
    db = TestingSessionLocal()
    
    # Import CSV sample data
    csv_path = Path(__file__).parent.parent / "data" / "wadrobe.csv"
    
    item1 = WardrobeItem(
        item_name="Oxford White Shirt",
        type="shirt",
        category="tops",
        color_name="white",
        reds=245, green=245, blue=245, hue=0.0,
        formality=9.0, vibe=["clean", "minimal"]
    )
    item2 = WardrobeItem(
        item_name="Grey Trousers",
        type="pants",
        category="bottoms",
        color_name="grey",
        reds=128, green=128, blue=128, hue=0.0,
        formality=9.0, vibe=["professional", "clean"]
    )
    item3 = WardrobeItem(
        item_name="Classic Silver Watch",
        type="watch",
        category="accessories",
        color_name="silver",
        reds=192, green=192, blue=192, hue=0.0,
        strap_reds=160, strap_green=160, strap_blue=160, strap_hue=0.0,
        dial_reds=255, dial_green=255, dial_blue=255, dial_hue=0.0,
        formality=9.0, vibe=["luxury", "clean"]
    )
    db.add_all([item1, item2, item3])
    db.commit()
    db.close()

    RecommendationService.invalidate_in_memory_engine()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_wardrobe_items(client):
    response = client.get("/api/v1/wardrobe/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert any(i["item_name"] == "Oxford White Shirt" for i in items)


def test_get_item_by_id(client):
    response = client.get("/api/v1/wardrobe/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["item_name"] == "Oxford White Shirt"


def test_create_update_delete_item(client):
    # 1. Create
    new_item = {
        "item_name": "Test Navy Blazer",
        "type": "jacket",
        "category": "tops",
        "color_name": "navy",
        "reds": 0, "green": 0, "blue": 128, "hue": 240.0,
        "formality": 8.0,
        "vibe": ["sharp", "formal"]
    }
    res_create = client.post("/api/v1/wardrobe/items", json=new_item)
    assert res_create.status_code == 201
    created_id = res_create.json()["id"]

    # 2. Update
    res_update = client.put(f"/api/v1/wardrobe/items/{created_id}", json={"formality": 9.0})
    assert res_update.status_code == 200
    assert res_update.json()["formality"] == 9.0

    # 3. Delete
    res_delete = client.delete(f"/api/v1/wardrobe/items/{created_id}")
    assert res_delete.status_code == 204

    # Confirm 404 on get
    res_get = client.get(f"/api/v1/wardrobe/items/{created_id}")
    assert res_get.status_code == 404


def test_recommendation_api(client):
    payload = {
        "required_types": ["shirt", "pants", "watch"],
        "strategy": "best"
    }
    res = client.post("/api/v1/recommendations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["strategy"] == "best"
    assert len(data["outfit"]) == 3
    assert data["score"] is not None
    assert data["score"] > 2.0


def test_legacy_endpoints_compatibility(client):
    res_items = client.get("/items")
    assert res_items.status_code == 200
    assert len(res_items.json()) == 3

    res_best = client.get("/best")
    assert res_best.status_code == 200
    assert "outfit" in res_best.json()
    assert "score" in res_best.json()

    res_stats = client.get("/graph/stats")
    assert res_stats.status_code == 200
    assert res_stats.json()["nodes"] == 3
