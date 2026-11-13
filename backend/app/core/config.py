from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/sqllab"
    jwt_secret: str = "change-me-in-production-use-32+chars"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 7
    admin_email: str = "admin@example.com"  # registering with this email grants role=admin
    otlp_endpoint: str = "http://otel-collector:4317"
    temporal_host: str = "temporal:7233"
    temporal_task_queue: str = "sql-lab-queue"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
