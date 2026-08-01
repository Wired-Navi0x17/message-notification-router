"""
Scam and Security Risk Detector for WhatsApp Message Notification Router.
High-priority security module that detects phishing, OTP theft, and domain spoofs,
enforcing an instant 'mute' override to protect users.
"""

from pydantic import BaseModel
from code.src.data.models import Message, ActionType, MessageType
from code.src.context.builder import EnrichedContext
from code.src.semantics.intent import SemanticFeatures


class ScamRiskAssessment(BaseModel):
    """Container for scam risk evaluation and safety override."""
    is_scam: bool = False
    risk_score: float = 0.0
    override_action: ActionType = "mute"
    override_message_type: MessageType = "scam"
    reason: str = ""


class ScamDetector:
    """Detects security threats, phishing attempts, and domain spoofing."""

    def evaluate_scam_risk(
        self,
        message: Message,
        context: EnrichedContext,
        semantics: SemanticFeatures
    ) -> ScamRiskAssessment:
        text_lower = semantics.unified_text.lower()
        risk_score = 0.0
        reasons = []

        # 1. OTP Theft / Sensitive Credentials Request
        if "enter otp" in text_lower or "share otp" in text_lower or "verification code" in text_lower:
            risk_score += 0.6
            reasons.append("Requests sensitive OTP or verification credentials.")

        # 2. Domain Mismatch / Brand Spoofing
        if context.business_context and context.business_context.is_domain_mismatched:
            risk_score += 0.5
            reasons.append(
                f"Sender domain ({context.business_context.domain_used_by_sender}) "
                f"does not match official brand domain ({context.business_context.official_domain})."
            )

        # 3. Phishing Keywords & Fake Fee Requests
        if any(w in text_lower for w in ["reattempt fee", "account suspended", "claim prize", "winner", "click link"]):
            risk_score += 0.4
            reasons.append("Contains suspicious phishing keywords or fake fee demands.")

        # 4. Unverified Sender asking for Money/OTP
        if context.business_context and not context.business_context.is_verified and semantics.is_payment:
            risk_score += 0.3
            reasons.append("Unverified sender requesting financial payment.")

        # 5. User Reports
        if context.business_context and context.business_context.user_reports_30d > 5:
            risk_score += 0.3
            reasons.append("Sender has high 30-day user report history.")

        is_scam = risk_score >= 0.5 or semantics.is_scam_suspicious

        if is_scam:
            summary_reason = "Suspicious scam or phishing risk detected: " + " ".join(reasons) if reasons else "High-risk scam pattern detected."
            return ScamRiskAssessment(
                is_scam=True,
                risk_score=min(1.0, round(risk_score, 2)),
                override_action="mute",
                override_message_type="scam",
                reason=summary_reason
            )

        return ScamRiskAssessment(is_scam=False, risk_score=round(risk_score, 2))
