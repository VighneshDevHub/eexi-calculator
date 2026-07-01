
import multiprocessing
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
workers = os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")
worker_connections = os.getenv("GUNICORN_WORKER_CONNECTIONS", 1000)
max_requests = os.getenv("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50)
timeout = os.getenv("GUNICORN_TIMEOUT", 30)
keepalive = os.getenv("GUNICORN_KEEPALIVE", 2)
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
