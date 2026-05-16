import os

DATABASE = os.environ.get("DATABASE_URL", "app.db")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))
AUTH_API_URL = os.environ.get("AUTH_API_URL", "https://auth-api.example.com")
EXTERNAL_API_URL = os.environ.get("EXTERNAL_API_URL", "https://api.example.com")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))
