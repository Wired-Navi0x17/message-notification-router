"""
Spam Detector for WhatsApp Message Notification Router.
Independent risk module that identifies viral forward noise, unrequested promotional blasts,
and sender identity metadata anomalies to enforce a 'mute' override.
"""

from pydantic import BaseModel
from code.src.data.models import Message, ActionType, MessageType
from code.src.context.builder import EnrichedContext
from code.src.semantics.intent import SemanticFeatures


class SpamRiskAssessment(BaseModel):
    """Container for spam risk evaluation and safety override."""
    is_spam: bool = False
    risk_score: float = 0.0
    override_action: ActionType = "mute"
    override_message_type: MessageType = "spam"
    reason: str = ""


class SpamDetector:
    """Detects viral forwards, unrequested promotions, and opt-out violations."""

    def evaluate_spam_risk(
        self,
        message: Message,
        context: EnrichedContext,
        semantics: SemanticFeatures
    ) -> SpamRiskAssessment:
        risk_score = 0.0
        reasons = []
        override_type: MessageType = "spam"

        # 1. High Forward Count (Viral Spam / Forward Noise)
        if "fwd as received" in semantics.unified_text.lower() or message.forwarded_count >= 10:
            risk_score += 0.6
            override_type = "forward"
            reasons.append("Highly forwarded message with potential viral spam noise.")
        elif message.forwarded_count >= 5 and semantics.is_promotion:
            risk_score += 0.4
            reasons.append("Forwarded promotional content.")

        # 2. Sender Identity Metadata Fusion (Unverified + High Reports + High Dismissals)
        if context.business_context and not context.business_context.is_verified:
            if context.business_context.user_reports_30d > 5:
                risk_score += 0.5
                reasons.append(f"Unverified sender with high 30-day user report history ({context.business_context.user_reports_30d} reports).")
            if context.business_context.user_messages_dismissed_30d >= 5:
                risk_score += 0.3
                reasons.append("User repeatedly dismissed previous messages from this sender.")

        # 3. Promotion Opt-Out Violation
        if context.business_context and not context.business_context.allows_promotions and semantics.is_promotion:
            risk_score += 0.6
            reasons.append("Sender sent promotional offer despite user opt-out preference.")

        # 4. Group Mute State
        if context.group_context and context.group_context.is_group_muted_by_user and not semantics.is_urgent:
            risk_score += 0.4
            reasons.append("Group is muted by user and message is non-urgent.")

        is_spam = risk_score >= 0.5

        if is_spam:
            summary_reason = "Unwanted spam noise detected: " + " ".join(reasons) if reasons else "High-volume spam pattern detected."
            return SpamRiskAssessment(
                is_spam=True,
                risk_score=min(1.0, round(risk_score, 2)),
                override_action="mute",
                override_message_type=override_type,
                reason=summary_reason
            )

        return SpamRiskAssessment(is_spam=False, risk_score=round(risk_score, 2))
