"""
Configuration module for VeriSerp AI Agent.
Handles environment variables, API key resolution, and runtime defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "VeriSerp AI — Multi-Engine Intelligence & Fact-Checking Agent"
    VERSION: str = "1.0.0"
    HACKATHON_NAME: str = "SerpApi India Hackathon 2026"
    
    # API Keys
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "").strip()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    
    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Defaults for SerpApi search tools
    DEFAULT_WEB_ENGINE: str = "google_light"
    DEFAULT_SECONDARY_ENGINE: str = "bing"
    MAX_SEARCH_RESULTS_PER_ENGINE: int = 6
    SEARCH_TIMEOUT: float = 15.0

    @classmethod
    def get_serpapi_key(cls, user_key: str | None = None) -> str:
        """Resolve SerpApi key: user-supplied in request overrides env var."""
        if user_key and user_key.strip():
            return user_key.strip()
        return cls.SERPAPI_API_KEY

    @classmethod
    def has_serpapi_key(cls, user_key: str | None = None) -> bool:
        return bool(cls.get_serpapi_key(user_key))

    @classmethod
    def get_llm_provider(cls) -> str:
        if cls.GEMINI_API_KEY:
            return "gemini"
        if cls.OPENAI_API_KEY:
            return "openai"
        if cls.GROQ_API_KEY:
            return "groq"
        return "native_heuristic"

settings = Settings()
