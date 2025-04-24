# k8s-helm-grafana

Practice repository to setup Kubernetes, Grafana and Prometheus with helm charts for a dummy application.

### Run it standalone:

```bash
docker run -d --name redis -p 6379:6379 redis
python3 -m venv venv
source venv/bin/activate
pip install flask redis
python3 app.py
```

Visit: http://localhost:5000

Every refresh will increment the Redis counter and show the updated count in the browser.
