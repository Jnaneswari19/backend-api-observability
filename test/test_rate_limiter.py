import time

class RateLimiter:
    def __init__(self, capacity=5, refill_rate=1):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        elapsed = now - self.last_refill
        refill = int(elapsed * self.refill_rate)
        if refill > 0:
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last_refill = now
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False
def test_rate_limiter_block_and_refill():
    limiter = RateLimiter(capacity=1, refill_rate=1)
    ip = "127.0.0.1"
    assert limiter.is_allowed(ip)      # first allowed
    assert not limiter.is_allowed(ip)  # second blocked
    import time
    time.sleep(1.1)
    assert limiter.is_allowed(ip)      # refilled
