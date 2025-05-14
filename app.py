from flask import Flask, jsonify, render_template, request
import redis
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
import time

# Create a custom registry
registry = CollectorRegistry()

app = Flask(__name__)
redis_host = os.environ.get('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0)

# Define Prometheus metrics with explicit registry
REQUEST_COUNT = Counter('app_request_count',
                        'Total app HTTP request count', registry=registry)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 'Request latency in seconds', registry=registry)
REDIS_COUNTER = Gauge('app_redis_counter',
                      'Current value of Redis counter', registry=registry)


@app.route('/')
def index():
    # Track request with Prometheus
    REQUEST_COUNT.inc()

    # Track latency
    start_time = time.time()

    # Increment Redis counter
    count = r.incr('counter')

    # Record Redis counter value using a Gauge
    REDIS_COUNTER.set(count)

    # Observe latency
    REQUEST_LATENCY.observe(time.time() - start_time)

    return render_template('index.html', count=count)


@app.route('/metrics')
def metrics():
    # Update the Redis counter value before generating metrics
    try:
        current_count = int(r.get('counter') or 0)
        REDIS_COUNTER.set(current_count)
    except (redis.exceptions.RedisError, ValueError):
        pass

    # Generate latest metrics from our custom registry
    return generate_latest(registry), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/crash')
def crash():
    """
    Endpoint that intentionally crashes the application to demonstrate 
    Kubernetes self-healing capabilities.
    """
    # Log that we're about to crash
    app.logger.error("Application crash triggered via /crash endpoint!")

    # Increment a counter to track crashes
    r.incr('crash_counter')

    # Exit with non-zero status to ensure the container fails
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        # Force crash the process
        os._exit(1)  # More forceful than sys.exit()
    return "Crashing application..."


if __name__ == '__main__':
    # Pre-initialize counter to ensure it appears in metrics
    REQUEST_COUNT.inc(0)
    app.run(debug=True, host='0.0.0.0')
