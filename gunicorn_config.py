"""Gunicorn configuration file for SDG Assessment application."""

import multiprocessing

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
# Calculate optimal workers: (CPU cores × 2) + 1
# Use fewer workers for development
workers = multiprocessing.cpu_count() * 2 + 1 if multiprocessing.cpu_count() <= 4 else 4
worker_class = "gthread"  # Better for I/O-bound operations than sync
threads = 4  # Number of threads per worker (total concurrent requests: workers × threads)
worker_connections = 1000
timeout = 120  # Increased from default 30 seconds
graceful_timeout = 30
keepalive = 5

# Restart workers after this many requests (prevents memory leaks)
max_requests = 5000  # Increased from 1000 for better performance
max_requests_jitter = 200  # Increased jitter proportionally

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "sdg-assessment"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload the app for memory efficiency (shares code between workers)
# Set to False in development if you need auto-reload
preload_app = True

# Reload when code changes (development only - disable in production)
reload = False  # Changed to False for production-like behavior
reload_engine = 'auto'

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server...")

def on_reload(server):
    """Called when workers are reloaded."""
    server.log.info("Reloading workers...")

def worker_int(worker):
    """Called when a worker receives an INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker times out."""
    worker.log.warning("Worker timeout - aborting")
