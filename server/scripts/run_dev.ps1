# Run development stack and seed demo data (PowerShell)
# Requires Docker Desktop with `docker` (or `docker compose`) available.

Set-Location -Path (Resolve-Path "${PSScriptRoot}\..\..")

Write-Host "Starting Docker Compose services..."
# Try modern `docker compose` first
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    docker compose up --build -d
} else {
    Write-Host "Docker CLI not found. Please install Docker Desktop and ensure 'docker' is on PATH."
    exit 1
}

Write-Host "Seeding demo data into backend..."
# Wait a few seconds for backend to be ready
Start-Sleep -Seconds 6
try {
    docker compose exec backend python /app/server/scripts/seed_demo.py
    docker compose exec backend python /app/server/scripts/seed_payments.py
    Write-Host "Seeding completed. Frontend should be available at http://localhost:3000"
} catch {
    Write-Host "Failed to execute seed scripts inside backend container. You can run them manually once the container is up: docker compose exec backend python /app/server/scripts/seed_demo.py"
}
