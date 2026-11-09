#!/usr/bin/env python
"""
Production WSGI Server for AI Cover Letter Generator.
Powered by Waitress - a production-quality, multi-threaded, hardened WSGI server.

Features:
- Multi-threaded asynchronous request processing
- Native cross-platform execution (Windows, Linux, macOS)
- Unified single-origin serving: serves compiled Vue 3 SPA + Flask REST API
- Hardened HTTP security headers
- Graceful shutdown and pre-flight configuration validation
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Ensure backend root is on Python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from app import create_app
from app.config import Config
from app.services.ai_service import AIService

logger = logging.getLogger("production_server")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run AI Cover Letter Generator on the production Waitress WSGI server."
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST") or os.getenv("FLASK_HOST", "0.0.0.0"),
        help="Host interface to bind (default: 0.0.0.0 or FLASK_HOST)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT") or os.getenv("FLASK_PORT", "5000")),
        help="Port to listen on (default: 5000 or PORT)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=int(os.getenv("WAITRESS_THREADS", "8")),
        help="Number of worker threads (default: 8)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run pre-flight checks and exit without starting the server"
    )
    return parser.parse_args()


def print_banner(host: str, port: int, threads: int, frontend_ready: bool):
    display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
    url = f"http://{display_host}:{port}"
    bind_url = f"http://{host}:{port}"

    print("=" * 72)
    print("      AI COVER LETTER GENERATOR - PRODUCTION SERVER (WAITRESS)     ")
    print("=" * 72)
    print(f"  • Status:              READY FOR PRODUCTION DEPLOYMENT")
    print(f"  • Bound Interface:     {bind_url}")
    print(f"  • Access URL:          {url}")
    print(f"  • Worker Threads:      {threads}")
    print(f"  • Model Configured:    {Config.GEMINI_MODEL}")
    print(f"  • Gemini Key Status:   {'Configured' if Config.GEMINI_API_KEY else 'Missing (Demo Mode only)'}")
    print(f"  • Demo Mode:           {'Enabled (Offline)' if Config.DEMO_MODE else 'Disabled (Production AI)'}")
    print(f"  • Static SPA Frontend: {'Integrated (Serving from frontend/dist)' if frontend_ready else 'API Only (Run npm run build first)'}")
    print("=" * 72)
    print(f"  Server listening on {bind_url}. Press Ctrl+C to terminate.")
    print("=" * 72)
    sys.stdout.flush()


def main():
    args = parse_args()

    # Pre-flight checks
    frontend_dist = Config.FRONTEND_DIST_DIR
    frontend_ready = frontend_dist.is_dir() and (frontend_dist / "index.html").is_file()

    # Create Flask application
    app = create_app(Config)

    if args.check:
        print("[PRE-FLIGHT] Checking Gemini connection status...")
        status, msg = AIService.test_connection()
        print(f"[PRE-FLIGHT] AI Connection Status: {status} ({msg})")
        print(f"[PRE-FLIGHT] Frontend Dist: {'OK' if frontend_ready else 'NOT FOUND'}")
        print("[PRE-FLIGHT] All pre-flight checks completed.")
        sys.exit(0)

    from waitress import serve
    print_banner(args.host, args.port, args.threads, frontend_ready)

    try:
        serve(
            app,
            host=args.host,
            port=args.port,
            threads=args.threads,
            ident="AICoverLetterGenerator/1.0"
        )
    except KeyboardInterrupt:
        print("\n[SERVER] Gracefully shutting down Waitress production server...")
        sys.exit(0)


if __name__ == "__main__":
    main()
