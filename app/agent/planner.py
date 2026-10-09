"""
Autonomous Deconstructive Planner.
Breaks down research topics and assertions into multi-engine search queries
and verification hypotheses.
"""
from dataclasses import dataclass, field
import re
from typing import Any

@dataclass
class SearchQueryPlan:
    query: str
    engine: str
    tool: str  # "web_search" | "news_search"
    purpose: str
    expected_signal: str

@dataclass
class ResearchPlan:
    original_claim: str
    intent_category: str  # "fact_check", "event_tracking", "market_intelligence", "tech_verification"
    core_entities: list[str]
    temporal_anchor: str
    verification_hypotheses: list[str]
    queries: list[SearchQueryPlan] = field(default_factory=list)
    depth: str = "balanced"

class DeconstructivePlanner:
    """
    Deconstructs claims and research topics into multi-angle search plans
    tailored for SerpApi's specialized engines.
    """

    STOP_WORDS = {
        "is", "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
        "did", "has", "have", "will", "what", "how", "why", "when", "who", "which"
    }

    def generate_plan(self, topic_or_claim: str, depth: str = "balanced") -> ResearchPlan:
        topic_clean = topic_or_claim.strip()
        intent = self._classify_intent(topic_clean)
        entities = self._extract_entities(topic_clean)
        temporal = self._extract_temporal_anchor(topic_clean)
        hypotheses = self._formulate_hypotheses(topic_clean, intent)

        queries: list[SearchQueryPlan] = []

        # 1. Primary Canonical Search (Google Light)
        queries.append(SearchQueryPlan(
            query=topic_clean,
            engine="google_light",
            tool="web_search",
            purpose="Authoritative Primary Search",
            expected_signal="Official announcements, documentation, and leading domain reporting"
        ))

        # 2. Freshness & Breaking News Search (Google News via news_search)
        news_q = self._construct_news_query(topic_clean, entities, temporal)
        queries.append(SearchQueryPlan(
            query=news_q,
            engine="google",
            tool="news_search",
            purpose="Real-time News & Recency Check",
            expected_signal="Current news coverage, press releases, and editorial reporting"
        ))

        # 3. Independent Cross-Verification Search (Bing via web_search)
        bing_q = self._construct_cross_check_query(topic_clean, entities)
        queries.append(SearchQueryPlan(
            query=bing_q,
            engine="bing",
            tool="web_search",
            purpose="Independent Cross-Engine Validation",
            expected_signal="Alternative search index ranking to avoid single-engine bias"
        ))

        # 4. If in-depth mode, add a counter-claim / scrutiny query
        if depth == "deep":
            counter_q = self._construct_counter_query(topic_clean, entities)
            queries.append(SearchQueryPlan(
                query=counter_q,
                engine="google_light",
                tool="web_search",
                purpose="Counter-Evidence & Skepticism Probe",
                expected_signal="Dissenting opinions, fact-checks, delays, debunking, or criticisms"
            ))

        return ResearchPlan(
            original_claim=topic_clean,
            intent_category=intent,
            core_entities=entities,
            temporal_anchor=temporal,
            verification_hypotheses=hypotheses,
            queries=queries,
            depth=depth
        )

    def _classify_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["did", "is it true", "fact check", "fake", "hoax", "really", "claim", "rumor"]):
            return "fact_check"
        if any(w in text_lower for w in ["launch", "released", "announced", "today", "yesterday", "breaking", "update"]):
            return "event_tracking"
        if any(w in text_lower for w in ["market", "valuation", "shares", "stock", "funding", "revenue", "price", "vs"]):
            return "market_intelligence"
        return "tech_verification"

    def _extract_entities(self, text: str) -> list[str]:
        # Extract capitalized phrases or key quoted tokens
        quoted = re.findall(r'"([^"]*)"', text)
        words = [w.strip(",.?!\"'") for w in text.split()]
        capitalized = [w for w in words if w and w[0].isupper() and w.lower() not in self.STOP_WORDS]
        
        entities = list(dict.fromkeys(quoted + capitalized))
        if not entities:
            # Fallback to non-stopwords
            entities = [w for w in words if w.lower() not in self.STOP_WORDS][:4]
        return entities[:5]

    def _extract_temporal_anchor(self, text: str) -> str:
        year_match = re.search(r'\b(202[0-9]|2030)\b', text)
        if year_match:
            return year_match.group(1)
        if any(w in text.lower() for w in ["latest", "recent", "today", "now", "current"]):
            return "2026 (Current)"
        return "2026"

    def _formulate_hypotheses(self, text: str, intent: str) -> list[str]:
        hypotheses = []
        if intent == "fact_check":
            hypotheses.append(f"H1: Substantive corroboration exists from tier-1 official sources regarding: '{text}'.")
            hypotheses.append(f"H2: Conflicting reporting or explicit debunking identifies this claim as inaccurate.")
        elif intent == "event_tracking":
            hypotheses.append("H1: Direct statements or regulatory filings confirm current operational status.")
            hypotheses.append("H2: Timeline revisions or external delays have been reported.")
        else:
            hypotheses.append(f"H1: Industry consensus validates market milestones and technological readiness.")
            hypotheses.append("H2: Commercialization obstacles or competing developments impact viability.")
        return hypotheses

    def _construct_news_query(self, text: str, entities: list[str], temporal: str) -> str:
        if entities:
            q = " ".join(entities[:3])
            if temporal and temporal not in q:
                q += f" {temporal}"
            return q
        return text

    def _construct_cross_check_query(self, text: str, entities: list[str]) -> str:
        if len(entities) >= 2:
            return f"{' '.join(entities[:3])} official announcement status"
        return f"{text} verified source"

    def _construct_counter_query(self, text: str, entities: list[str]) -> str:
        if entities:
            return f"{' '.join(entities[:3])} fact check controversy dispute debunked"
        return f"{text} fact check dispute"
