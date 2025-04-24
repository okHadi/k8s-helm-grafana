FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Explicitly set host to 0.0.0.0 to make it accessible from outside the container
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
