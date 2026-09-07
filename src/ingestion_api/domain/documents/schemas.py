from enum import StrEnum

class SourceType(StrEnum):
    PRIMARY_REGULATION = "primary_regulation"
    REGULATORY_GUIDANCE = "regulatory_guidance"
    OFFICIAL_REPORT = "official_report"
    MARKET_REPORT = "market_report"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"

SOURCE_WEIGHTS = {
    SourceType.PRIMARY_REGULATION: 1.0,
    SourceType.REGULATORY_GUIDANCE: 0.9,
    SourceType.OFFICIAL_REPORT: 0.8,
    SourceType.MARKET_REPORT: 0.6,
    SourceType.TECHNICAL_REPORT: 0.7,
    SourceType.OTHER: 0.5,
}
