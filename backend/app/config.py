from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    cookie_secure: bool = False

    admin_username: str = ""
    admin_password: str = ""

    upload_dir: Path = BASE_DIR / "uploads"
    upload_max_mb: int = 50
    static_dir: Path = BASE_DIR / "static"

    discovery_enabled: bool = True
    discovery_mdns: bool = True
    discovery_snmp: bool = False
    discovery_subnets: str = ""
    discovery_interval: int = 300
    snmp_community: str = "public"
    job_sync_enabled: bool = True
    job_sync_interval: int = 15
    timezone: str = "Europe/Berlin"

    cups_pdf_queue: str = ""

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
