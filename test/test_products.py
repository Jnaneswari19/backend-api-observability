from api.src.services.product_service import ProductService
from api.src.models.product import Product

def test_product_model_to_dict():
    product = Product("Phone", "Smartphone", 800)
    data = product.to_dict()
    assert data["name"] == "Phone"
    assert data["description"] == "Smartphone"
    assert data["price"] == 800

def test_product_service_add_and_list():
    service = ProductService()
    product = service.add_product("Tablet", "Android tablet", 500)
    assert product["name"] == "Tablet"
    products = service.get_all_products()
    assert len(products) == 1
    assert products[0]["name"] == "Tablet"

def test_create_product_success(client):
    response = client.post("/api/products", json={
        "name": "Laptop",
        "description": "Gaming laptop",
        "price": 1200
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["name"] == "Laptop"

def test_create_product_invalid(client):
    response = client.post("/api/products", json={"name": "Laptop"})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_list_products(client):
    client.post("/api/products", json={
        "name": "Phone",
        "description": "Smartphone",
        "price": 500
    })
    response = client.get("/api/products")
    assert response.status_code == 200
    products = response.get_json()
    assert isinstance(products, list)
    assert len(products) >= 1
