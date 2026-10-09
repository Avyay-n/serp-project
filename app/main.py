"""
FastAPI application for VeriSerp AI Agent.
Serves interactive Web UI and REST API endpoints for agent research workflows.
"""
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent import VeriSerpAgent
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Engine Intelligence & Fact-Checking Agent built for SerpApi India Hackathon 2026"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Claim, topic, or question to investigate")
    depth: str = Field(default="balanced", description="'balanced' or 'deep'")
    api_key: Optional[str] = Field(default=None, description="Optional SerpApi key to override environment")
    force_simulation: bool = Field(default=False, description="Whether to run in demo simulation mode")

class KeyTestRequest(BaseModel):
    api_key: str = Field(..., description="SerpApi API key to validate")

@app.get("/")
async def root():
    """Serves the main web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found")
    return FileResponse(index_file)

@app.post("/api/research")
async def conduct_research(req: ResearchRequest):
    """
    Executes an autonomous multi-engine investigation.
    Deconstructs claim -> runs SerpApi web & news searches -> verifies consensus -> synthesizes dossier.
    """
    try:
        agent = VeriSerpAgent(api_key=req.api_key)
        result = await agent.run_investigation(
            topic_or_claim=req.query,
            depth=req.depth,
            force_simulation=req.force_simulation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research agent failed: {str(e)}")

@app.post("/api/test-key")
async def test_api_key(req: KeyTestRequest):
    """
    Validates a SerpApi key by testing against SerpApi.
    """
    key = req.api_key.strip()
    if not key:
        return {"valid": False, "message": "Key is empty."}
    try:
        from serpapi import Client
        client = Client(api_key=key)
        # Attempt minimal light search
        res = client.search({"engine": "google_light", "q": "test", "num": 1})
        if "error" in res:
            return {"valid": False, "message": res.get("error")}
        return {"valid": True, "message": "SerpApi key successfully validated and active!"}
    except Exception as e:
        return {"valid": False, "message": str(e)}

@app.get("/api/templates")
async def get_templates():
    """
    Returns curated showcase prompts for the SerpApi India Hackathon 2026.
    """
    return [
        {
            "id": "semi-india",
            "category": "National Tech & Manufacturing",
            "title": "Tata & PSMC Dholera Fab 2026 Timeline",
            "query": "Tata Electronics Dholera semiconductor fab commercial chip production 2026 timeline and partner status",
            "badge": "Semiconductor Mission"
        },
        {
            "id": "isro-mission",
            "category": "Space & Defense",
            "title": "ISRO Gaganyaan Crewed Flight 2026 Schedule",
            "query": "ISRO Gaganyaan uncrewed test flight and crewed orbital mission schedule status 2026",
            "badge": "Space Research"
        },
        {
            "id": "ai-models",
            "category": "AI & LLM Frontiers",
            "title": "OpenAI o3 and DeepSeek Reasoning Benchmarks",
            "query": "OpenAI o3 reasoning model benchmarks math and coding vs DeepSeek R1 2026",
            "badge": "AI Benchmarks"
        },
        {
            "id": "quantum-rumor",
            "category": "Fact-Check Probe",
            "title": "Claim: Commercial 100-Qubit Quantum Computer in India",
            "query": "Did India commercially deploy a 100 qubit quantum computer in early 2026?",
            "badge": "Fact-Check"
        }
    ]

@app.get("/api/status")
async def get_status():
    """
    Returns agent configuration and system health status.
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "hackathon": settings.HACKATHON_NAME,
        "serpapi_key_configured": bool(settings.SERPAPI_API_KEY),
        "llm_provider": settings.get_llm_provider(),
        "default_web_engine": settings.DEFAULT_WEB_ENGINE,
        "default_secondary_engine": settings.DEFAULT_SECONDARY_ENGINE,
        "mcp_enabled": True
    }
