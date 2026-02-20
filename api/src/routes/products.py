# api/src/routes/products.py
from flask import Blueprint, request, jsonify
from loguru import logger

products_bp = Blueprint("products", __name__)
products = []

@products_bp.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    description = data.get("description")
    price = data.get("price")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Product name must be a non-empty string"}), 400
    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "Product description must be a non-empty string"}), 400
    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Product price must be a positive number"}), 400

    product = {
        "id": len(products) + 1,
        "name": name.strip(),
        "description": description.strip(),
        "price": price
    }
    products.append(product)

    logger.info({"event": "product_added", "product_id": product["id"]})
    return jsonify(product), 201

@products_bp.route("/api/products", methods=["GET"])
def list_products():
    logger.info({"event": "list_products", "count": len(products)})
    return jsonify(products), 200

def test_create_product_missing_name(client):
    resp = client.post("/api/products", json={"description": "Smartphone", "price": 500})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_product_missing_description(client):
    resp = client.post("/api/products", json={"name": "Phone", "price": 500})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_product_invalid_price(client):
    resp = client.post("/api/products", json={"name": "Phone", "description": "Smartphone", "price": -10})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_product_no_json(client):
    resp = client.post("/api/products", data="notjson", content_type="text/plain")
    assert resp.status_code == 400
    assert "error" in resp.get_json()
