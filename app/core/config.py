from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepMediaCheck"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]

    # Fusion Weights - Optimized for accuracy (Visual Classifier prioritized)
    WEIGHT_METADATA: float = 0.15
    WEIGHT_ARTIFACTS: float = 0.15
    WEIGHT_CLASSIFIER: float = 0.7
    
    # Gemini / Explanations
    GEMINI_API_KEY: str = ""
    ENABLE_LLM_EXPLANATIONS: bool = False

    # Database & Security
    MONGO_URI: str = "mongodb://localhost:27017" # Default to local, user can override in .env
    MONGODB_URL: str = None # Alias for users who put MONGODB_URL in .env
    DATABASE_NAME: str = "deepmediacheck"
    SECRET_KEY: str = "your-secret-key-change-it-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
