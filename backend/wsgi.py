"""
Standard WSGI entry point for AI Cover Letter Generator.
Compatible with all WSGI servers: Waitress, Gunicorn, uWSGI, mod_wsgi, AWS Elastic Beanstalk.

Usage Examples:
    Waitress (Cross-Platform / Windows):
        python serve.py

    Gunicorn (Linux / Container):
        gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from app import create_app
from app.config import Config

app = create_app(Config)

if __name__ == "__main__":
    from waitress import serve
    host = Config.FLASK_HOST
    port = Config.FLASK_PORT
    threads = Config.WAITRESS_THREADS
    print(f"Starting Waitress on http://{host}:{port} ({threads} threads)...")
    serve(app, host=host, port=port, threads=threads)
