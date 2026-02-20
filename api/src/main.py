from flask import Flask, request, jsonify
from loguru import logger
from prometheus_client import Counter, generate_latest
from api.src.middleware.rate_limiter import rate_limit_middleware
from api.src.routes.products import products_bp   # ✅ import blueprint

logger.remove()
logger.add(sink=lambda msg: print(msg, end=""), serialize=True)

app = Flask(__name__)
app.register_blueprint(products_bp)   # ✅ register blueprint

# Prometheus metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests", ["endpoint", "method"])
RATE_LIMIT_HITS = Counter("rate_limit_hits_total", "Total rate limit hits")

@app.before_request
def before_request():
    REQUEST_COUNT.labels(endpoint=request.path, method=request.method).inc()
    logger.info({"event": "request_received", "method": request.method, "path": request.path})
    if request.path == "/api/protected-action":
        result = rate_limit_middleware()
        if result:
            RATE_LIMIT_HITS.inc()
            logger.warning({"event": "rate_limit_triggered", "client_ip": request.remote_addr})
            return result

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/protected-action", methods=["POST"])
def protected_action():
    data = request.get_json()
    logger.info({"event": "protected_action", "data": data})
    return jsonify({"message": "Protected action executed", "data": data}), 200

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
