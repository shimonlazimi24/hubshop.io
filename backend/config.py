from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "frodo"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # Database
    database_url: str = "postgresql+asyncpg://frodo:frodo@localhost:5432/frodo"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # Token Vault
    token_vault_key: str = Field(
        default="change-me-base64-encoded-32-byte-key",
        description="Base64-encoded 32-byte AES-256-GCM key for token encryption",
    )

    # TikTok Shop
    tiktok_shop_app_key: str = ""
    tiktok_shop_app_secret: str = ""

    # TikTok Shop SDK Sidecar
    tiktok_shop_sdk_url: str = "http://localhost:4000"
    sidecar_auth_token: str = ""

    # TikTok Developer
    tiktok_developer_client_key: str = ""
    tiktok_developer_client_secret: str = ""

    # TikTok Marketing
    tiktok_marketing_app_id: str = ""
    tiktok_marketing_app_secret: str = ""

    # TikTok Research API
    tiktok_research_client_key: str = ""
    tiktok_research_client_secret: str = ""

    # Google OAuth (for social login)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # TikTok Login (social login — distinct from Developer platform connect)
    tiktok_login_redirect_uri: str = "http://localhost:8000/api/auth/tiktok/callback"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @model_validator(mode="after")
    def _check_production_secrets(self) -> "Settings":
        """Block production startup if secret keys still have insecure defaults."""
        if self.app_env == "production":
            insecure_keys: list[str] = []
            if "change-me" in self.secret_key:
                insecure_keys.append("SECRET_KEY")
            if "change-me" in self.jwt_secret_key:
                insecure_keys.append("JWT_SECRET_KEY")
            if "change-me" in self.token_vault_key:
                insecure_keys.append("TOKEN_VAULT_KEY")
            if insecure_keys:
                raise ValueError(
                    f"Insecure default values detected for: {', '.join(insecure_keys)}. "
                    "Set strong secret keys before running in production."
                )
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
