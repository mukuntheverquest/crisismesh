"""
CrisisMesh Configuration - Open Agent Hackathon 2026
Centralized settings management with Pydantic
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "CrisisMesh"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SAMPLE_MODE: bool = True
    DEBUG: bool = True

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "crisismesh"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crisismesh"
    SQLITE_URL: str = "sqlite:///./data/crisismesh.db"

    @property
    def effective_database_url(self) -> str:
        if self.SAMPLE_MODE:
            return self.SQLITE_URL
        return self.DATABASE_URL

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # Zetaris
    ZETARIS_URL: str = "http://localhost:8080"
    ZETARIS_API_KEY: str = ""
    ZETARIS_ORG_ID: str = ""
    ZETARIS_WORKSPACE_ID: str = ""

    # Meterless
    METERLESS_API_URL: str = "https://api.meterless.io"
    METERLESS_API_KEY: str = ""
    METERLESS_PROJECT_ID: str = ""
    METERLESS_ENVIRONMENT: str = "development"

    @property
    def METERLESS_URL(self) -> str:
        return self.METERLESS_API_URL

    # NVIDIA
    NVIDIA_VISIBLE_DEVICES: str = "0"
    CUDA_VISIBLE_DEVICES: str = "0"
    NVIDIA_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    NVIDIA_LLM_MODEL: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    NVIDIA_TENSORRT_OPTIMIZATION: bool = True
    NVIDIA_BATCH_SIZE: int = 32
    
    @property
    def USE_GPU(self) -> bool:
        """Check if GPU acceleration is enabled"""
        import os
        return (
            os.environ.get("CUDA_VISIBLE_DEVICES", "0") != "-1" and
            os.environ.get("NVIDIA_VISIBLE_DEVICES", "0") != "-1"
        )

    # LLM Providers
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434/v1"
    LOCAL_LLM_MODEL: str = "llama3.1:8b"

    # External Data Sources
    NWS_API_URL: str = "https://api.weather.gov"
    USGS_API_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1"
    COPERNICUS_API_URL: str = "https://catalogue.dataspace.copernicus.eu"
    HOTOSM_API_URL: str = "https://api.hotosm.org"
    SENTINEL_HUB_API_URL: str = "https://services.sentinel-hub.com"

    # Alert Systems
    IPAWS_API_URL: str = "https://api.ipaws.gov"
    ES_ALERT_API_URL: str = ""
    GENSAS_API_URL: str = ""

    # Frontend
    VITE_API_BASE_URL: str = "http://localhost:8000/api/v1"
    VITE_WS_URL: str = "ws://localhost:8000/ws"
    VITE_MAPBOX_TOKEN: str = ""

    # Security
    SECRET_KEY: str = "your_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Agent Configuration
    AGENT_CHECKPOINT_DIR: str = "./checkpoints"
    AGENT_MAX_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 300
    PLANNER_MODEL: str = "gpt-4o-mini"
    EVALUATOR_MODEL: str = "gpt-4o-mini"
    RISK_MODEL: str = "gpt-4o-mini"

    # Disaster-specific
    ALERT_DEADMAN_SWITCH_SECONDS: int = 180
    POLYGON_EXPANSION_FACTOR: float = 1.5
    MULTI_MODAL_CONFIDENCE_THRESHOLD: float = 0.75
    GEOCODING_HALLUCINATION_THRESHOLD: float = 0.04
    OFFLINE_MODE_ENABLED: bool = True

    # Asset Catalog
    ASSET_CATALOG_REFRESH_HOURS: int = 24
    DRONE_ASSET_MIN_COUNT: int = 3
    TUNNEL_RESCUE_ASSET_REQUIRED: bool = True

    # Quality Thresholds
    MIN_QUALITY_SCORE: float = 0.7
    MAX_REVISION_LOOPS: int = 3
    CONTENT_PRESERVATION_THRESHOLD: float = 0.8


settings = Settings()


# Export for backward compatibility
__all__ = ["settings", "Settings"]