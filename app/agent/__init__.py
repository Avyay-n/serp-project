"""
VeriSerp Agent Package.
Exposes the end-to-end autonomous research and fact-checking agent.
"""
import time
from typing import Any

from app.agent.planner import DeconstructivePlanner, ResearchPlan
from app.agent.search_service import MultiEngineSearchService, QueryExecutionResult
from app.agent.verifier import EvidenceVerifier, VerificationMatrix
from app.agent.synthesizer import DossierSynthesizer, ResearchDossier

class VeriSerpAgent:
    """
    Autonomous multi-engine intelligence & fact-checking agent.
    Deconstructs -> Searches across SerpApi engines -> Verifies consensus -> Synthesizes.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.planner = DeconstructivePlanner()
        self.search_service = MultiEngineSearchService(api_key=api_key)
        self.verifier = EvidenceVerifier()
        self.synthesizer = DossierSynthesizer()

    async def run_investigation(
        self,
        topic_or_claim: str,
        depth: str = "balanced",
        force_simulation: bool = False
    ) -> dict[str, Any]:
        start_overall = time.perf_counter()

        # Step 1: Query & Hypothesis Planning
        plan = self.planner.generate_plan(topic_or_claim, depth=depth)

        # Step 2: Parallel Multi-Engine Search Execution
        query_results = await self.search_service.execute_plan(
            plan.queries,
            force_simulation=force_simulation
        )

        # Step 3: Evidence Cross-Referencing & Consensus Matrix
        matrix = self.verifier.verify(topic_or_claim, query_results)

        # Step 4: Analytical Synthesis Dossier
        dossier = await self.synthesizer.generate_dossier(plan, matrix)

        total_latency = round((time.perf_counter() - start_overall) * 1000, 1)

        # Structure full response for Web UI and API clients
        return {
            "query": topic_or_claim,
            "depth": depth,
            "total_latency_ms": total_latency,
            "plan": {
                "intent": plan.intent_category,
                "entities": plan.core_entities,
                "temporal_anchor": plan.temporal_anchor,
                "hypotheses": plan.verification_hypotheses,
                "planned_queries_count": len(plan.queries)
            },
            "queries_executed": [
                {
                    "query": qr.plan.query,
                    "engine": qr.plan.engine,
                    "tool": qr.plan.tool,
                    "purpose": qr.plan.purpose,
                    "success": qr.success,
                    "latency_ms": qr.latency_ms,
                    "results_count": len(qr.items),
                    "is_simulated": qr.is_simulated,
                    "error": qr.error_message
                }
                for qr in query_results
            ],
            "verification": {
                "verdict_code": matrix.verdict_code,
                "verdict_label": matrix.verdict_label,
                "badge_color": matrix.verdict_badge_color,
                "consensus_score": matrix.consensus_score,
                "confidence_level": matrix.confidence_level,
                "summary": matrix.summary_verdict,
                "total_sources_evaluated": matrix.total_sources_evaluated,
                "unique_domains_count": matrix.unique_domains_count,
                "engine_coverage": matrix.engine_coverage,
                "domain_distribution": matrix.domain_breakdown,
                "key_quote": matrix.key_corroborating_quote
            },
            "evidence": {
                "supporting": [self._serialize_item(it) for it in matrix.supporting_evidence],
                "counter": [self._serialize_item(it) for it in matrix.counter_evidence],
                "nuanced": [self._serialize_item(it) for it in matrix.nuanced_evidence]
            },
            "dossier": {
                "executive_summary": dossier.executive_summary,
                "markdown_report": dossier.markdown_report,
                "provider_used": dossier.provider_used,
                "sources_cited": dossier.sources_cited
            }
        }

    def _serialize_item(self, item: Any) -> dict[str, Any]:
        return {
            "id": item.id,
            "title": item.title,
            "link": item.link,
            "snippet": item.snippet,
            "source": item.source,
            "domain": item.domain,
            "date": item.date,
            "engine": item.engine,
            "tool": item.tool,
            "credibility_tier": item.credibility_tier,
            "stance": item.stance
        }

__all__ = ["VeriSerpAgent", "DeconstructivePlanner", "MultiEngineSearchService", "EvidenceVerifier", "DossierSynthesizer"]
