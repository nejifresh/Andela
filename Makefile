.PHONY: backend-install frontend-install api frontend test eval demo docker-build docker-up docker-down

backend-install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

api:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && PYTHONPATH=. pytest -q

eval:
	cd backend && PYTHONPATH=. python3 scripts/eval.py

demo:
	@echo "Terminal 1: make api"
	@echo "Terminal 2: make frontend"
	@echo "Open http://localhost:3000 and upload backend/sample_data/aws_resources.csv plus azure_resources.csv"

docker-build:
	docker build -f backend/Dockerfile -t cloudwaste-api:local .
	docker build -f frontend/Dockerfile --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 -t cloudwaste-dashboard:local .

docker-up:
	docker compose up --build

docker-down:
	docker compose down
