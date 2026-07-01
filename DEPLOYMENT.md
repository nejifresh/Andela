# Deployment Guide

CloudWaste Sentinel is packaged as two containers:

- `backend/Dockerfile`: FastAPI API, SQLite by default.
- `frontend/Dockerfile`: Next.js dashboard, built with `NEXT_PUBLIC_API_BASE_URL`.

The MVP is still generate-only: it does not call cloud provider APIs and does not execute remediation commands.

## Local Docker

```bash
docker compose up --build
```

Open:

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

## Google Cloud Run

Deploy the API first:

```bash
gcloud builds submit --project PROJECT_ID --config cloudbuild.backend.yaml .
gcloud run deploy cloudwaste-api \
  --image gcr.io/PROJECT_ID/cloudwaste-api \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=sqlite:////tmp/cloudwaste.db,CORS_ORIGINS=https://DASHBOARD_URL
```

Then build the dashboard with the deployed API URL:

```bash
gcloud builds submit \
  --project PROJECT_ID \
  --config cloudbuild.frontend.yaml \
  --substitutions _API_URL=https://API_URL .
gcloud run deploy cloudwaste-dashboard \
  --image gcr.io/PROJECT_ID/cloudwaste-dashboard \
  --region us-central1 \
  --allow-unauthenticated
```

For a real Cloud Run deployment, replace SQLite with Cloud SQL Postgres or another managed database. SQLite on `/tmp` is ephemeral and suitable only for demo sessions.

## AWS ECS

Recommended ECS shape:

- One service/task for `cloudwaste-api`.
- One service/task for `cloudwaste-dashboard`.
- Application Load Balancer routes public traffic to the dashboard and API.
- API environment variables:
  - `DATABASE_URL=sqlite:////data/cloudwaste.db` for demo only.
  - `CORS_ORIGINS=https://dashboard.example.com`.
- Dashboard build argument:
  - `NEXT_PUBLIC_API_BASE_URL=https://api.example.com`.

Build and push images to ECR:

```bash
aws ecr create-repository --repository-name cloudwaste-api
aws ecr create-repository --repository-name cloudwaste-dashboard

docker build -f backend/Dockerfile -t ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/cloudwaste-api:latest .
docker build \
  -f frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_API_BASE_URL=https://api.example.com \
  -t ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/cloudwaste-dashboard:latest .

aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/cloudwaste-api:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/cloudwaste-dashboard:latest
```

For persistent ECS demo storage, mount EFS at `/data`. For production, use Postgres and SQLAlchemy migrations.

## Operational Notes

- `NEXT_PUBLIC_API_BASE_URL` is a build-time value for browser code. Rebuild the frontend image when the API URL changes.
- Cloud Run and ECS both inject `PORT`; both Dockerfiles honor it.
- Do not expose this MVP as a production system with SQLite unless the deployment is explicitly a single-session demo.
- The generated remediation commands still require human review and are never executed by the application.
