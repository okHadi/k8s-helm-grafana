from flask import Flask, jsonify, render_template
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/')
def index():
    count = r.incr('counter')
    return render_template('index.html', count=count)

if __name__ == '__main__':
    app.run(debug=True)
