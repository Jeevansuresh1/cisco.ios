import os

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_TOKEN_EXPIRY = int(os.environ.get("JWT_TOKEN_EXPIRY", 3600))
JWT_REFRESH_EXPIRY = int(os.environ.get("JWT_REFRESH_EXPIRY", 86400))
JWT_ALGORITHM = "HS256"
AUTH_EXEMPT_PATHS = ["/login", "/health", "/"]
