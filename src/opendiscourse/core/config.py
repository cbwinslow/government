from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Core application settings.
    This is the industry standard for managing configurations and secrets in Python.
    By using pydantic-settings, we ensure that:
    1. Types are validated (e.g. integer ports are actually integers).
    2. We can load from a local .env file during development.
    3. In production or for other users, they can just pass environment variables directly
       without needing a physical .env file.
    """
    
    # Project Info
    PROJECT_NAME: str = "OpenDiscourse"
    VERSION: str = "0.1.0"
    
    # Database
    POSTGRES_USER: str = "govadmin"
    POSTGRES_PASSWORD: str = "govpassword"
    POSTGRES_DB: str = "govdata"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Qdrant Vector Store
    QDRANT_URL: str = "http://localhost:6333"
    
    # API Keys for External Services
    # These are marked Optional because the application should still boot
    # even if a user hasn't supplied all keys (they just won't be able to run specific scrapers).
    CONGRESS_API_KEY: Optional[str] = None
    OPENSTATES_API_KEY: Optional[str] = None
    OPENSECRETS_API_KEY: Optional[str] = None
    VOTESMART_API_KEY: Optional[str] = None
    
    # LLM Stack
    OPENROUTER_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # SSH / ZeroTier (client/server setup)
    # If behind an SSH tunnel or ZeroTier, set this to the reachable host/IP
    # so the dashboard and visualization tools can connect from your local machine.
    # Example: HOST="0.0.0.0" or HOST="172.25.10.64"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # This config tells Pydantic to read from a local .env file if it exists.
    # extra="ignore" ensures that if a user has extra variables in their environment, it doesn't crash.
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Constructs the Postgres connection string from components."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# Instantiate a global settings object to be imported throughout the app
settings = Settings()
