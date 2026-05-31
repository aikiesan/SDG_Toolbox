#!/bin/sh
set -e

echo "===================="
echo "Starting SDG Assessment Application"
echo "Environment: ${FLASK_ENV:-development}"
echo "===================="

# Wait for database to be ready
echo "Waiting for database..."
MAX_RETRIES=${DB_WAIT_RETRIES:-10}
RETRIES=0
until nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}" 2>/dev/null; do
  RETRIES=$((RETRIES + 1))
  if [ "$RETRIES" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: Could not reach database at ${DB_HOST:-db}:${DB_PORT:-5432} after $MAX_RETRIES attempts — aborting startup."
    exit 1
  fi
  echo "Database is unavailable - sleeping ($RETRIES/$MAX_RETRIES)"
  sleep 2
done
echo "Database is up!"

# Run migrations with timeout
echo "Running database migrations..."
export FLASK_APP=run
timeout 60 flask db upgrade || {
    echo "Migration failed or timed out"
    exit 1
}

echo "Migrations complete!"

# Seed required SDG reference data (idempotent — skips if already present).
# Without this the questionnaire/goals are empty and the core feature fails.
if [ "${SKIP_SEED:-false}" != "true" ]; then
    echo "Seeding SDG reference data..."
    flask populate-goals || echo "WARNING: populate-goals failed (continuing)"
    flask populate-questions || echo "WARNING: populate-questions failed (continuing)"
    echo "Seeding complete!"
else
    echo "SKIP_SEED=true — skipping SDG reference data seeding."
fi

# Start server with appropriate configuration based on environment
echo "Starting Gunicorn server..."
if [ "$FLASK_ENV" = "production" ]; then
    echo "Using production configuration (gunicorn_config.prod.py)"
    exec gunicorn --config gunicorn_config.prod.py run:app
else
    echo "Using development configuration (gunicorn_config.py)"
    exec gunicorn --config gunicorn_config.py run:app
fi
