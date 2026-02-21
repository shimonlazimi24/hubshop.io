import os

# Set test environment variables before any imports
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://frodo:frodo@localhost:5432/frodo_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-jwt")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
# 32-byte key base64-encoded for tests
os.environ.setdefault("TOKEN_VAULT_KEY", "dGVzdC1rZXktMzItYnl0ZXMtbG9uZy0xMjM0NTY=")
os.environ.setdefault("TIKTOK_SHOP_APP_KEY", "test_shop_key")
os.environ.setdefault("TIKTOK_SHOP_APP_SECRET", "test_shop_secret")
os.environ.setdefault("TIKTOK_DEVELOPER_CLIENT_KEY", "test_dev_key")
os.environ.setdefault("TIKTOK_DEVELOPER_CLIENT_SECRET", "test_dev_secret")
os.environ.setdefault("TIKTOK_MARKETING_APP_ID", "test_marketing_id")
os.environ.setdefault("TIKTOK_MARKETING_APP_SECRET", "test_marketing_secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_google_client_id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_google_secret")
