import os
import sys

# Ensure backend root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    print(f"Starting AI Cover Letter Generator Backend on http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"Gemini Model Configured: {Config.GEMINI_MODEL}")
    print(f"Demo Mode: {Config.DEMO_MODE}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=True
    )
