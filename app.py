from flask import Flask, jsonify, render_template
import redis
import os

app = Flask(__name__)
redis_host = os.environ.get('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0)

@app.route('/')
def index():
    count = r.incr('counter')
    return render_template('index.html', count=count)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
