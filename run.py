"""
VeriSerp AI — Launch Script
Starts the FastAPI application and development server.
"""
import sys
import uvicorn
from app.config import settings

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 70)
    print(">> VeriSerp AI -- Multi-Engine Intelligence & Fact-Checking Agent")
    print("   Built for SerpApi India Hackathon 2026")
    print("=" * 70)
    print(f"-> Dashboard URL:   http://{settings.HOST}:{settings.PORT}")
    print(f"-> SerpApi Key:     {'CONFIGURED in .env' if settings.SERPAPI_API_KEY else 'NOT SET (Demo mode available)'}")
    print(f"-> Synthesizer:     {settings.get_llm_provider().upper()}")
    print("=" * 70)
    print("Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

if __name__ == "__main__":
    main()
