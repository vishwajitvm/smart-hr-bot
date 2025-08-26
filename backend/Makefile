.PHONY: install run dev lint test docker-up docker-down logs

# Install dependencies
install:
	pip install --upgrade pip && pip install -r requirements.txt

# Run FastAPI locally
run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Run with Docker
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

# Logs
logs:
	docker-compose logs -f backend

# Code quality
lint:
	flake8 app

# Run tests
test:
	pytest -v --disable-warnings
