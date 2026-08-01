"""
Priority Scoring Matrix for WhatsApp Message Notification Router.
Calculates multi-dimensional Utility, Urgency, and Risk scores for decision fusion.
"""

from pydantic import BaseModel
from code.src.data.models import Message
from code.src.context.builder import EnrichedContext
from code.src.semantics.intent import SemanticFeatures
from code.src.trust.engine import PersonalizedTrustScore


class PriorityMatrix(BaseModel):
    """Container for multi-dimensional priority scores."""
    utility_score: float = 0.5
    urgency_score: float = 0.5
    risk_score: float = 0.0


class PriorityScorer:
    """Computes Utility, Urgency, and Risk matrix scores."""

    def compute_priority(
        self,
        message: Message,
        context: EnrichedContext,
        semantics: SemanticFeatures,
        trust: PersonalizedTrustScore
    ) -> PriorityMatrix:
        text_lower = semantics.unified_text.lower()
        conv_type = message.conversation_type.strip().lower()

        # 1. URGENCY SCORE COMPUTATION
        urgency = semantics.intent_scores.get("urgent", 0.0)
        if any(w in text_lower for w in ["tanker", "heads-up", "heads up", "valve", "unwell", "clinic", "incident bridge", "emergency", "leaving 15 mins early"]):
            urgency = max(urgency, 0.85)
        if semantics.has_direct_user_mention:
            urgency = max(urgency, 0.80)

        # 2. UTILITY SCORE COMPUTATION
        utility = 0.30
        if conv_type == "business" and trust.business_trust.is_trusted:
            if any(w in text_lower for w in ["order", "packed", "delivery", "hub", "shipped", "amazon", "health"]):
                utility += 0.50
        elif conv_type == "group":
            if trust.group_trust.is_sender_admin:
                utility += 0.40
            if semantics.has_direct_user_mention:
                utility += 0.40
            if any(w in text_lower for w in ["tanker", "water supply", "bus", "pickup"]):
                utility += 0.40
        elif conv_type == "personal":
            utility += 0.40

        if trust.overall_trust_score >= 0.70:
            utility += 0.20

        # 3. RISK SCORE COMPUTATION
        risk = 0.0
        if semantics.is_scam_suspicious or trust.business_trust.domain_mismatched:
            risk = 0.95
        elif context.business_context and context.business_context.user_reports_30d > 0:
            risk = 0.50
        elif message.forwarded_count >= 10:
            risk = 0.60
        elif semantics.is_promotion and not trust.business_trust.allows_promotions:
            risk = 0.70

        return PriorityMatrix(
            utility_score=max(0.0, min(1.0, round(utility, 2))),
            urgency_score=max(0.0, min(1.0, round(urgency, 2))),
            risk_score=max(0.0, min(1.0, round(risk, 2))),
        )
