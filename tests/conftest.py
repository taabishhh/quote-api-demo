import os

# Config the app needs at import time. Set before the app module is imported.
os.environ.setdefault("UPSTREAM_URL", "https://example.test/fact")
os.environ.setdefault("APP_VERSION", "test")
