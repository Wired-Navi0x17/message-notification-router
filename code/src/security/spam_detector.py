"""
Spam Detector for WhatsApp Message Notification Router.
Independent risk module that identifies viral forward noise, unrequested promotional blasts,
and opt-out violations to enforce a 'mute' override.
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

        # 1. High Forward Count (Viral Spam)
        if message.forwarded_count >= 10:
            risk_score += 0.6
            reasons.append("Highly forwarded message with potential viral spam noise.")
        elif message.forwarded_count >= 5 and semantics.is_promotion:
            risk_score += 0.4
            reasons.append("Forwarded promotional content.")

        # 2. Promotion Opt-Out Violation
        if context.business_context and not context.business_context.allows_promotions and semantics.is_promotion:
            risk_score += 0.6
            reasons.append("Sender sent promotional offer despite user opt-out preference.")

        # 3. High Dismissal History
        if context.business_context and context.business_context.user_messages_dismissed_30d >= 5 and context.business_context.user_messages_replied_30d == 0:
            risk_score += 0.3
            reasons.append("User repeatedly dismissed previous messages from this sender.")

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
                override_message_type="spam",
                reason=summary_reason
            )

        return SpamRiskAssessment(is_spam=False, risk_score=round(risk_score, 2))
