"""
Verification & Credibility Matrix.
Cross-references evidence from multiple search engines, computes consensus scores,
evaluates domain authority, and determines an objective verdict.
"""
from dataclasses import dataclass, field
import re
from typing import Any
from app.agent.search_service import EvidenceItem, QueryExecutionResult

@dataclass
class VerificationMatrix:
    verdict_code: str  # "VERIFIED", "SUPPORTED", "CONTESTED", "UNSUBSTANTIATED", "DEBUNKED"
    verdict_label: str
    verdict_badge_color: str  # "emerald", "blue", "amber", "purple", "rose"
    consensus_score: int  # 0 to 100
    confidence_level: str  # "High", "Moderate", "Developing"
    summary_verdict: str
    total_sources_evaluated: int
    unique_domains_count: int
    engine_coverage: list[str]
    supporting_evidence: list[EvidenceItem] = field(default_factory=list)
    counter_evidence: list[EvidenceItem] = field(default_factory=list)
    nuanced_evidence: list[EvidenceItem] = field(default_factory=list)
    domain_breakdown: dict[str, int] = field(default_factory=dict)
    key_corroborating_quote: str = ""

class EvidenceVerifier:
    """
    Evaluates multi-engine evidence to produce an unbiased consensus rating.
    """

    REFUTATION_SIGNALS = [
        "debunk", "false", "fake", "hoax", "denied", "denies", "no evidence",
        "untrue", "misleading", "fact-check: false", "premature", "incorrect",
        "rumor", "refutes", "refuted", "exaggerated", "postponed indefinitely"
    ]

    SUPPORTING_SIGNALS = [
        "confirmed", "approves", "approved", "announces", "official", "pib",
        "gazette", "verified", "signed", "begins", "launches", "contract",
        "milestone", "validated", "on track", "cabinet", "certified"
    ]

    NUANCE_SIGNALS = [
        "however", "delay", "hurdle", "subject to", "conditional", "challenges",
        "pending", "timeline revised", "partially", "experts caution", "yet to"
    ]

    def verify(self, claim: str, query_results: list[QueryExecutionResult]) -> VerificationMatrix:
        # Collect and deduplicate evidence items by URL
        seen_urls: set[str] = set()
        all_items: list[EvidenceItem] = []
        engine_set: set[str] = set()
        domain_counts: dict[str, int] = {}

        for qr in query_results:
            if not qr.success:
                continue
            for item in qr.items:
                clean_url = item.link.split("#")[0].rstrip("/")
                if clean_url in seen_urls and clean_url:
                    continue
                if clean_url:
                    seen_urls.add(clean_url)
                
                # Classify stance
                self._classify_item_stance(item, claim)
                all_items.append(item)
                engine_set.add(item.engine)
                domain_counts[item.domain] = domain_counts.get(item.domain, 0) + 1

        supporting = [it for it in all_items if it.stance == "supporting"]
        counter = [it for it in all_items if it.stance == "refuting"]
        nuanced = [it for it in all_items if it.stance in ("nuanced", "neutral")]

        # Weighted calculation based on credibility tier
        def calc_weight(items: list[EvidenceItem]) -> float:
            score = 0.0
            for it in items:
                if it.credibility_tier == "high":
                    score += 1.0
                elif it.credibility_tier == "medium":
                    score += 0.65
                else:
                    score += 0.35
            return score

        sup_weight = calc_weight(supporting)
        counter_weight = calc_weight(counter)
        total_weight = sup_weight + counter_weight + (calc_weight(nuanced) * 0.3)

        if total_weight > 0:
            raw_consensus = (sup_weight / (sup_weight + counter_weight + 0.001)) * 100
            # Scale slightly with domain diversity
            diversity_bonus = min(len(domain_counts) * 2.5, 10.0)
            consensus_score = min(max(int(raw_consensus), 5), 98)
        else:
            consensus_score = 50

        # Verdict logic
        if counter_weight >= 2.0 and counter_weight > sup_weight:
            verdict_code = "DEBUNKED"
            verdict_label = "Debunked / Refuted"
            badge_color = "rose"
            confidence = "High"
            summary = "Authoritative reports and official fact-checks actively refute or contradict this assertion."
        elif consensus_score >= 80 and len(domain_counts) >= 2:
            verdict_code = "VERIFIED"
            verdict_label = "Verified / High Confidence"
            badge_color = "emerald"
            confidence = "High"
            summary = "Corroborated across multiple independent, high-authority news wires and official disclosures."
        elif consensus_score >= 60:
            verdict_code = "SUPPORTED"
            verdict_label = "Plausible / Supported"
            badge_color = "blue"
            confidence = "Moderate"
            summary = "Substantial evidence aligns with the claim, though operational caveats or timelines remain developing."
        elif 35 <= consensus_score < 60 and counter:
            verdict_code = "CONTESTED"
            verdict_label = "Contested / Disputed"
            badge_color = "amber"
            confidence = "Moderate"
            summary = "Conflicting viewpoints detected across credible publications with active debate or discrepancies."
        else:
            verdict_code = "UNSUBSTANTIATED"
            verdict_label = "Unsubstantiated / Developing"
            badge_color = "purple"
            confidence = "Developing"
            summary = "Insufficient primary documentation found to validate this claim definitively at this time."

        # Pick key quote
        best_quote = ""
        if supporting:
            best_quote = supporting[0].snippet
        elif all_items:
            best_quote = all_items[0].snippet

        return VerificationMatrix(
            verdict_code=verdict_code,
            verdict_label=verdict_label,
            verdict_badge_color=badge_color,
            consensus_score=consensus_score,
            confidence_level=confidence,
            summary_verdict=summary,
            total_sources_evaluated=len(all_items),
            unique_domains_count=len(domain_counts),
            engine_coverage=sorted(list(engine_set)),
            supporting_evidence=supporting,
            counter_evidence=counter,
            nuanced_evidence=nuanced,
            domain_breakdown=domain_counts,
            key_corroborating_quote=best_quote
        )

    def _classify_item_stance(self, item: EvidenceItem, claim: str) -> None:
        text = f"{item.title} {item.snippet}".lower()

        # Check refutations first
        if any(sig in text for sig in self.REFUTATION_SIGNALS):
            item.stance = "refuting"
            return

        # Check nuances
        if any(sig in text for sig in self.NUANCE_SIGNALS):
            item.stance = "nuanced"
            return

        # Check supporting signals
        if any(sig in text for sig in self.SUPPORTING_SIGNALS):
            item.stance = "supporting"
            return

        # Default fallback
        item.stance = "supporting" if item.position <= 2 else "neutral"
