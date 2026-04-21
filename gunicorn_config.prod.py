"""
Production Gunicorn configuration for SDG Assessment Tool
Optimized for VPS-1 (2 vCPU, 4GB RAM)
"""

import multiprocessing
import os

# Worker processes
# Production: (CPU cores × 2) + 1, capped at 4 (Railway has fewer CPUs)
cpu_count = multiprocessing.cpu_count()
workers = int(os.environ.get('WEB_CONCURRENCY', min(cpu_count * 2 + 1, 4)))

# Use threaded workers for better I/O performance
worker_class = "gthread"
threads = 4  # 4 threads per worker (total concurrent: workers × threads)
worker_connections = 1000
timeout = 60  # Stricter timeout for production (60s vs 120s)
graceful_timeout = 30
keepalive = 5

# Memory management
# Restart workers after processing this many requests to prevent memory leaks
max_requests = 5000  # Increased from 1000
max_requests_jitter = 250

# PRODUCTION settings - no reload, enable preload for memory efficiency
reload = False
preload_app = True  # Share code between workers

# Performance tuning
sendfile = True
reuse_port = True
backlog = 2048

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Server mechanics
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Process naming
proc_name = "sdg-assessment"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Forwarded headers (when behind proxy/load balancer)
forwarded_allow_ips = '*'
proxy_allow_ips = '*'

# Callbacks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info(
        f"Starting Gunicorn (production) - "
        f"Workers: {workers}, Threads: {threads}, "
        f"Capacity: {workers * threads} concurrent requests"
    )

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn server ready")

def worker_abort(worker):
    """Called when a worker times out."""
    worker.log.error(f"Worker {worker.pid} timeout - aborting")

def on_exit(server):
    """Called just before the master process exits."""
    server.log.info("Gunicorn shutting down")
