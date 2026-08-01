"""
Business Trust Scorer for WhatsApp Message Notification Router.
Calculates quantitative trust scores for business senders based on verification,
domain validation, account age, and user relationship history.
"""

from pydantic import BaseModel
from code.src.context.builder import EnrichedContext, BusinessContext


class BusinessTrustAssessment(BaseModel):
    """Container for business trust metrics."""
    trust_score: float = 0.5
    is_verified: bool = False
    is_trusted: bool = False
    allows_promotions: bool = True
    domain_mismatched: bool = False
    relationship_type: str = ""


class BusinessTrustScorer:
    """Evaluates legitimacy and trust score of business senders."""

    def evaluate_business_trust(self, context: EnrichedContext) -> BusinessTrustAssessment:
        biz = context.business_context
        if not biz:
            return BusinessTrustAssessment()

        score = 0.30  # Baseline

        # Verified Account Boost (+0.35)
        if biz.is_verified:
            score += 0.35

        # Domain Validation Boost (+0.25) / Penalty (-0.50)
        if biz.is_domain_mismatched:
            score -= 0.50
        elif biz.official_domain and biz.official_domain == biz.domain_used_by_sender:
            score += 0.25

        # Account Age Boost
        if biz.account_age_days >= 365:
            score += 0.15
        elif biz.account_age_days >= 90:
            score += 0.05

        # User Relationship Boost (+0.20)
        if biz.user_activity_count_180d > 0 or biz.relationship_reason:
            score += 0.20

        # User Report Penalty (-0.30)
        if biz.user_reports_30d > 0:
            score -= (biz.user_reports_30d * 0.10)

        final_score = max(0.0, min(1.0, round(score, 2)))
        is_trusted = final_score >= 0.65 and not biz.is_domain_mismatched

        return BusinessTrustAssessment(
            trust_score=final_score,
            is_verified=biz.is_verified,
            is_trusted=is_trusted,
            allows_promotions=biz.allows_promotions,
            domain_mismatched=biz.is_domain_mismatched,
            relationship_type=biz.relationship_reason,
        )
