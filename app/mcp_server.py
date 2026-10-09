"""
VeriSerp FastMCP Server.
Exposes autonomous multi-engine search and fact-checking capabilities
as standard Model Context Protocol (MCP) tools for Claude Desktop, Cursor, and VS Code.
"""
import asyncio
from typing import Any
from fastmcp import FastMCP
from app.agent import VeriSerpAgent
from app.config import settings

mcp = FastMCP(
    name="VeriSerp Intelligence Agent",
)

agent = VeriSerpAgent()

@mcp.tool()
async def veriserp_research(
    topic_or_claim: str,
    depth: str = "balanced"
) -> dict[str, Any]:
    """
    Autonomously investigates a research topic or breaking claim using SerpApi
    multi-engine search (Google Light, Bing, Google News).
    Returns an intelligence dossier, consensus rating, and verified sources.
    
    Args:
        topic_or_claim: The question, news claim, or market trend to research.
        depth: "balanced" for standard fast multi-engine search, or "deep" for counter-evidence probing.
    """
    result = await agent.run_investigation(topic_or_claim, depth=depth)
    return {
        "verdict": result["verification"]["verdict_label"],
        "consensus_score": result["verification"]["consensus_score"],
        "confidence_level": result["verification"]["confidence_level"],
        "summary": result["verification"]["summary"],
        "executive_summary": result["dossier"]["executive_summary"],
        "markdown_report": result["dossier"]["markdown_report"],
        "sources_cited": result["dossier"]["sources_cited"]
    }

@mcp.tool()
async def veriserp_verify_claim(claim: str) -> dict[str, Any]:
    """
    Rapidly verifies an assertion against live SerpApi web and news results.
    Computes an objective consensus score (0-100%) and credibility breakdown.
    
    Args:
        claim: Specific assertion to fact-check.
    """
    result = await agent.run_investigation(claim, depth="balanced")
    verif = result["verification"]
    return {
        "claim": claim,
        "verdict": verif["verdict_label"],
        "consensus_score": verif["consensus_score"],
        "confidence": verif["confidence_level"],
        "key_quote": verif["key_quote"],
        "sources_count": verif["total_sources_evaluated"],
        "unique_domains": verif["unique_domains_count"]
    }

@mcp.tool()
async def veriserp_multi_search(query: str) -> dict[str, Any]:
    """
    Performs parallel web and news search using serpapi-search-tools across
    Google and Bing indexes, returning normalized, high-signal results.
    """
    from app.agent.planner import SearchQueryPlan
    plans = [
        SearchQueryPlan(
            query=query,
            engine="google_light",
            tool="web_search",
            purpose="Web Index",
            expected_signal="Authoritative sites"
        ),
        SearchQueryPlan(
            query=query,
            engine="google",
            tool="news_search",
            purpose="News Index",
            expected_signal="Recent coverage"
        )
    ]
    results = await agent.search_service.execute_plan(plans)
    serialized_results = []
    for r in results:
        for item in r.items:
            serialized_results.append({
                "title": item.title,
                "link": item.link,
                "snippet": item.snippet,
                "source": item.source,
                "date": item.date,
                "engine": item.engine
            })
    return {"results": serialized_results[:10]}

if __name__ == "__main__":
    mcp.run()
