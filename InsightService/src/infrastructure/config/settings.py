from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ======================
    # Database (MySQL)
    # ======================
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # ======================
    # RabbitMQ
    # ======================
    rabbitmq_host: str = Field(default="localhost", env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(default="guest", env="RABBITMQ_USER")
    rabbitmq_password: str = Field(default="guest", env="RABBITMQ_PASSWORD")
    rabbitmq_queue: str = Field(default="transaction_processed", env="RABBITMQ_QUEUE")
    rabbitmq_prefetch_count: int = Field(default=1, env="RABBITMQ_PREFETCH_COUNT")
    rabbitmq_mgmt_port: Optional[int] = Field(default=None, env="RABBITMQ_MGMT_PORT")
    
    # ======================
    # LLM (Ollama)
    # ======================
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    llm_model: str = Field(default="llama3.1:8b", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_timeout: int = Field(default=120, env="LLM_TIMEOUT")
    max_insights: int = Field(default=5, env="MAX_INSIGHTS")

    # ======================
    # Logging
    # ======================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # ======================
    # API HTTP (Health Check)
    # ======================
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8002, env="API_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # ✅ Prevents Pydantic from failing on extra vars


def get_settings() -> Settings:
    """Factory function to get settings instance"""
    return Settings()
