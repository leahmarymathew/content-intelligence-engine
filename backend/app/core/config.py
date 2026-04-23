import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralized runtime settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI Content Intelligence Engine"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./content.db")
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # RAG / Vector Stores
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "content-intelligence")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "content-intelligence")
    RAG_DEFAULT_TOP_K: int = int(os.getenv("RAG_DEFAULT_TOP_K", "5"))
    RAG_MAX_RETRIES: int = int(os.getenv("RAG_MAX_RETRIES", "2"))
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        return [origin.strip() for origin in origins.split(",")]
    
    # Server
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

settings = Settings()

# Legacy support for direct import
OPENAI_API_KEY = settings.OPENAI_API_KEY