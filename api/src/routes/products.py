from flask import Blueprint, request, jsonify
from api.src.services.product_service import ProductService

products_bp = Blueprint("products", __name__)
service = ProductService()

@products_bp.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if "name" not in data or "description" not in data or "price" not in data:
        return jsonify({"error": "Missing required fields: name, description, price"}), 400
    if not isinstance(data["price"], (int, float)) or data["price"] <= 0:
        return jsonify({"error": "Price must be a positive number"}), 400
    if not isinstance(data["name"], str) or not data["name"].strip():
        return jsonify({"error": "Product name must be a non-empty string"}), 400
    if not isinstance(data["description"], str) or not data["description"].strip():
        return jsonify({"error": "Product description must be a non-empty string"}), 400

    product = service.add_product(data["name"], data["description"], data["price"])
    return jsonify(product), 201

@products_bp.route("/api/products", methods=["GET"])
def list_products():
    return jsonify(service.get_all_products()), 200
