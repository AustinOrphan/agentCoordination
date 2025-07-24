import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_product_data():
    return {
        "name": "Test Product",
        "description": "A test product for testing",
        "price": 29.99,
        "category_id": 1,
        "stock_quantity": 100
    }

def test_create_product(test_product_data):
    response = client.post("/api/products/", json=test_product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_product_data["name"]
    assert data["price"] == test_product_data["price"]

def test_get_products():
    response = client.get("/api/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_product():
    # First create a product
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 29.99,
        "category_id": 1,
        "stock_quantity": 100
    }
    create_response = client.post("/api/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]