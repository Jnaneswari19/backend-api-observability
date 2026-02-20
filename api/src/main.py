from flask import Flask, request, jsonify
from loguru import logger
from prometheus_client import Counter, generate_latest
from api.src.middleware.rate_limiter import rate_limit_middleware

# ✅ Configure loguru to output JSON structured logs
logger.remove()  # remove default handler
logger.add(
    sink=lambda msg: print(msg, end=""),
    serialize=True  # outputs logs as JSON
)

app = Flask(__name__)

# In-memory store for products
products = []

# Prometheus metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["endpoint", "method"])
RATE_LIMIT_HITS = Counter("rate_limit_hits_total", "Total rate limit hits")

@app.before_request
def before_request():
    REQUEST_COUNT.labels(endpoint=request.path, method=request.method).inc()
    logger.info({
        "event": "request_received",
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr
    })

    # Apply rate limiting only to protected endpoint
    if request.path == "/api/protected-action":
        result = rate_limit_middleware()
        if result:
            RATE_LIMIT_HITS.inc()
            logger.warning({
                "event": "rate_limit_triggered",
                "client_ip": request.remote_addr,
                "path": request.path
            })
            return result

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    # ✅ Validation
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

    # ✅ Persistence (in-memory list)
    product = {
        "id": len(products) + 1,
        "name": name.strip(),
        "description": description.strip(),
        "price": price
    }
    products.append(product)

    logger.info({
        "event": "product_added",
        "product_id": product["id"],
        "name": product["name"],
        "price": product["price"]
    })

    return jsonify(product), 201

@app.route("/api/products", methods=["GET"])
def list_products():
    logger.info({
        "event": "list_products",
        "count": len(products)
    })
    return jsonify(products), 200

@app.route("/api/protected-action", methods=["POST"])
def protected_action():
    data = request.get_json()
    logger.info({
        "event": "protected_action",
        "data": data
    })
    return jsonify({"message": "Protected action executed", "data": data}), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    # ✅ Run on all interfaces, port 8080
    app.run(host="0.0.0.0", port=8080)
