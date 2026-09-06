from enum import StrEnum

class SourceType(StrEnum):
    PRIMARY_REGULATION = "primary_regulation"
    REGULATORY_GUIDANCE = "regulatory_guidance"
    OFFICIAL_REPORT = "official_report"
    MARKET_REPORT = "market_report"
    OTHER = "other"
