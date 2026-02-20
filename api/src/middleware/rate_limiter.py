import time
import redis
from flask import request, jsonify

# Connect to Redis (service name from docker-compose.yml)
r = redis.Redis(host="redis", port=6379, db=0)

RATE_LIMIT = 5       # max requests
WINDOW = 60          # time window in seconds

def rate_limit_middleware():
    client_ip = request.remote_addr
    key = f"rate_limit:{client_ip}"
    now = int(time.time())

    # Get current count and window start from Redis
    data = r.get(key)
    if data:
        count, window_start = map(int, data.decode().split(":"))
    else:
        count, window_start = 0, now

    # Reset window if expired
    if now - window_start >= WINDOW:
        count, window_start = 0, now

    if count >= RATE_LIMIT:
        reset_time = window_start + WINDOW
        remaining = max(0, RATE_LIMIT - count)
        response = jsonify({"error": "Too Many Requests"})
        response.status_code = 429
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time - now)
        return response

    # Increment counter and persist in Redis
    count += 1
    r.set(key, f"{count}:{window_start}", ex=WINDOW)

    # Attach headers to normal responses
    def add_headers(response):
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - count)
        response.headers["X-RateLimit-Reset"] = str(window_start + WINDOW - now)
        return response

    return None  # allow request to continue
