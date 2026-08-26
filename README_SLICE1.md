AP Payment Fraud Sentinel — Slice 1 Scaffold

This repository contains a slice of the AP Payment Fraud Sentinel project focusing on:
- Authentication (register/login)
- Organization creation
- Simple dashboard

The scaffold includes:
- Backend: FastAPI + SQLAlchemy
- Frontend: Vite + React + TypeScript (minimal pages)
- docker-compose with Postgres and Redis

Important: This is Slice 1 of the full product. Follow the development strategy in the master prompt to continue.

Quickstart (requires Docker & Docker Compose):

1. Copy environment file:
   cp server/.env.example server/.env
   (On Windows, create server\\.env with the same contents)

2. Start services:
   docker compose up --build

3. Backend will be available at http://localhost:8000
   Frontend at http://localhost:3000

Seeding demo data (convenience):
- After services are up, run the seed scripts to populate a demo organization, user, vendors, and a payment sample.
  - Using Docker Compose:
    docker compose exec backend python /app/server/scripts/seed_demo.py
    docker compose exec backend python /app/server/scripts/seed_payments.py

- Or use the convenience PowerShell script:
  - From server/scripts run: ./run_dev.ps1

Notes:
- The backend creates DB tables on startup for dev convenience. For production use Alembic migrations.
- SECRET_KEY in .env must be replaced with a secure random value before production.
- This slice is intentionally minimal; next steps include vendors, invoices, risk engine, AI abstraction, and full RBAC.
