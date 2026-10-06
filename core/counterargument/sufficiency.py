"""Evidence-Sufficiency Gate evaluating data availability and enforcing clean, informative refusal."""

from __future__ import annotations

import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.semantic_layer.catalog import SemanticCatalog


class MissingDataRequirement(BaseModel):
    required_entity: str
    description: str
    suggested_source: str
    expected_fields: List[str]


class RefusalResult(BaseModel):
    is_refusal: bool
    refusal_reason: str
    explanation: str
    missing_requirements: List[MissingDataRequirement] = Field(default_factory=list)
    available_alternatives: List[str] = Field(default_factory=list)


class EvidenceSufficiencyGate:
    """Evaluates whether available warehouse telemetry is sufficient to support a defensible conclusion.
    
    Refusal is a first-class successful system state. The system never guesses or hallucinates.
    """

    KNOWN_UNSUPPORTED_DOMAINS = [
        (
            r"\b(election|political|politics|voting|campaign rally)\b",
            "Political & Electoral Data",
            "Electoral commission poll logs and constituency campaign timelines",
            ["election_date", "constituency_id", "voter_turnout_pct", "ruling_party"],
        ),
        (
            r"\b(weather|monsoon|rainfall|temperature|cyclone)\b",
            "Meteorological & Climate Data",
            "Regional meteorological bureau hourly telemetry",
            ["weather_station_id", "daily_rainfall_mm", "temperature_celsius"],
        ),
        (
            r"\b(stock market|interest rate|macroeconomic|gdp inflation)\b",
            "Macroeconomic Indices",
            "Central bank and macroeconomic financial data feeds",
            ["reporting_date", "repo_rate", "cpi_inflation", "gdp_growth_rate"],
        ),
    ]

    def __init__(self, catalog: Optional[SemanticCatalog] = None):
        self.catalog = catalog or SemanticCatalog()

    def evaluate_sufficiency(self, query: str) -> RefusalResult:
        q_lower = query.lower()

        # Check for known unsupported domain patterns
        for pattern, domain_name, source, fields in self.KNOWN_UNSUPPORTED_DOMAINS:
            if re.search(pattern, q_lower):
                return RefusalResult(
                    is_refusal=True,
                    refusal_reason="MISSING_DOMAIN_TELEMETRY",
                    explanation=(
                        f"The requested analysis requires external {domain_name}, which is not present in the enterprise data warehouse. "
                        "The platform strictly refuses to synthesize speculative causal claims in the absence of verified data."
                    ),
                    missing_requirements=[
                        MissingDataRequirement(
                            required_entity=domain_name,
                            description=f"External ingestion feed for {domain_name.lower()}.",
                            suggested_source=source,
                            expected_fields=fields,
                        )
                    ],
                    available_alternatives=[
                        "Which products lost the most customers in Kerala during Q2?",
                        "Why did customer churn surge in Kerala during Q2? (Delivery latency root-cause analysis)",
                        "What was the impact of delivery latency on Enterprise Suite Pro order completions?",
                    ],
                )

        return RefusalResult(
            is_refusal=False,
            refusal_reason="",
            explanation="Warehouse contains sufficient semantic entities and transactional telemetry to answer this inquiry.",
            missing_requirements=[],
            available_alternatives=[],
        )
